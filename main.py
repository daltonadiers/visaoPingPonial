# main.py
import cv2, time, collections
import mediapipe as mp
from gestures import classify_hand
from scorer import Scorer

mp_hands = mp.solutions.hands

DEBOUNCE_FRAMES = 6
COOLDOWN_S = 1.0        
PENDING_TTL = 3.0       
HOLD_REQUEST_FRAMES = 5 
HOLD_CONFIRM_FRAMES = 5 
RELEASE_FRAMES = 2      
ARM_DOWN_Y_THR = 0.60   

class Pending:
    def __init__(self, who: str, action: str):
        self.who = who      
        self.action = action
        self.t0 = time.time()

def main():
    cap = cv2.VideoCapture(1)
    hands = mp_hands.Hands(model_complexity=0, max_num_hands=4, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    scorer = Scorer()
    last_applied = {'A':0.0, 'B':0.0}
    pending: Pending | None = None

    state = {
        'A': {'up_top':0, 'down_bottom':0, 'confirm_top':0, 'relax_up':0, 'relax_down':0, 'lock_add':False, 'lock_sub':False},
        'B': {'up_top':0, 'down_bottom':0, 'confirm_top':0, 'relax_up':0, 'relax_down':0, 'lock_add':False, 'lock_sub':False},
    }

    while True:
        ok, frame = cap.read()
        if not ok: break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = hands.process(rgb)

        hand_states = []
        if res.multi_hand_landmarks and res.multi_handedness:
            for lm, hd in zip(res.multi_hand_landmarks, res.multi_handedness):
                handed = hd.classification[0].label  # "Left"/"Right"
                hand_states.append(classify_hand(lm, handed))

        H, W = frame.shape[:2]
        mid_y = 0.5 

        a_up_top_cnt = sum(1 for h in hand_states if h.x < 0.5 and h.y < mid_y and getattr(h, 'is_arm_up', False))
        b_up_top_cnt = sum(1 for h in hand_states if h.x >= 0.5 and h.y < mid_y and getattr(h, 'is_arm_up', False))

        a_down_bottom_present = any(
            (h.x < 0.5) and ((h.y >= ARM_DOWN_Y_THR) or (h.y >= mid_y and not getattr(h,'is_arm_up', False)))
            for h in hand_states
        )
        b_down_bottom_present = any(
            (h.x >= 0.5) and ((h.y >= ARM_DOWN_Y_THR) or (h.y >= mid_y and not getattr(h,'is_arm_up', False)))
            for h in hand_states
        )


        if a_up_top_cnt >= 1:
            state['A']['up_top'] += 1
            state['A']['relax_up'] = 0
        else:
            state['A']['up_top'] = 0
            state['A']['relax_up'] += 1

        if a_down_bottom_present:
            state['A']['down_bottom'] += 1
            state['A']['relax_down'] = 0
        else:
            state['A']['down_bottom'] = 0
            state['A']['relax_down'] += 1

        if b_up_top_cnt >= 1:
            state['B']['up_top'] += 1
            state['B']['relax_up'] = 0
        else:
            state['B']['up_top'] = 0
            state['B']['relax_up'] += 1

        if b_down_bottom_present:
            state['B']['down_bottom'] += 1
            state['B']['relax_down'] = 0
        else:
            state['B']['down_bottom'] = 0
            state['B']['relax_down'] += 1

        state['A']['confirm_top'] = state['A']['confirm_top'] + 1 if a_up_top_cnt >= 2 else 0
        state['B']['confirm_top'] = state['B']['confirm_top'] + 1 if b_up_top_cnt >= 2 else 0

        if state['A']['relax_up'] >= RELEASE_FRAMES:
            state['A']['lock_add'] = False
        if state['A']['relax_down'] >= RELEASE_FRAMES:
            state['A']['lock_sub'] = False
        if state['B']['relax_up'] >= RELEASE_FRAMES:
            state['B']['lock_add'] = False
        if state['B']['relax_down'] >= RELEASE_FRAMES:
            state['B']['lock_sub'] = False

        now = time.time()


        if pending is None:
            if state['A']['down_bottom'] >= HOLD_REQUEST_FRAMES and not state['A']['lock_sub'] and now - last_applied['A'] > COOLDOWN_S:
                pending = Pending('A', 'SUB')
                state['A']['lock_sub'] = True
            elif state['B']['down_bottom'] >= HOLD_REQUEST_FRAMES and not state['B']['lock_sub'] and now - last_applied['B'] > COOLDOWN_S:
                pending = Pending('B', 'SUB')
                state['B']['lock_sub'] = True

            elif state['A']['up_top'] >= HOLD_REQUEST_FRAMES and not state['A']['lock_add'] and now - last_applied['A'] > COOLDOWN_S:
                pending = Pending('A', 'ADD')
                state['A']['lock_add'] = True
            elif state['B']['up_top'] >= HOLD_REQUEST_FRAMES and not state['B']['lock_add'] and now - last_applied['B'] > COOLDOWN_S:
                pending = Pending('B', 'ADD')
                state['B']['lock_add'] = True

        if pending:

            if pending.who == 'A' and state['B']['confirm_top'] >= HOLD_CONFIRM_FRAMES:
                action = 'PLUS1' if pending.action=='ADD' else 'MINUS1'
                scorer.apply('A', action)
                last_applied['A'] = now
                pending = None
            elif pending.who == 'B' and state['A']['confirm_top'] >= HOLD_CONFIRM_FRAMES:
                action = 'PLUS1' if pending.action=='ADD' else 'MINUS1'
                scorer.apply('B', action)
                last_applied['B'] = now
                pending = None


        if pending and now - pending.t0 > PENDING_TTL:
            pending = None


        cv2.rectangle(frame, (10,10), (750,190), (0,0,0), -1)
        cv2.putText(frame, f"A: {scorer.a}   B: {scorer.b}", (20,55), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3)
        cv2.putText(frame, f"Topo: +1 (1 braço por {HOLD_REQUEST_FRAMES}f) -> Confirmar: 2 braços por {HOLD_CONFIRM_FRAMES}f", (20,95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,50), 1)
        cv2.putText(frame, f"Base: -1 (mão bem embaixo y>={int(ARM_DOWN_Y_THR*100)}%) -> Confirmar: 2 braços no topo {HOLD_CONFIRM_FRAMES}f", (20,120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,50), 1)
        if pending:
            op = '+1' if pending.action=='ADD' else '-1'
            cv2.putText(frame, f"Pedido {pending.who} ({op}): aguardando 2 braços no topo do oponente", (20,150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,220,50), 2)


        H, W = frame.shape[:2]
        cv2.line(frame, (W//2, 0), (W//2, H), (80,80,80), 1)
        cv2.line(frame, (0, H//2), (W, H//2), (80,80,80), 1)

        cv2.imshow("PingPong Gestures", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()

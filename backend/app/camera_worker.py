import threading
import time
import cv2
import mediapipe as mp
from app.state import state, state_lock

def camera_loop():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FPS, 30)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.5)
    mp_draw = mp.solutions.drawing_utils

    proposal = {"side": None, "time": 0.0, "gesture": None}
    PROPOSAL_TIMEOUT = 3.0
    COOLDOWN = 1.0
    last_score_time = 0.0
    HOLD_FRAMES = 6
    counts = {
        'left_one': 0, 'left_thumbs': 0, 'left_min': 0,
        'right_one': 0, 'right_thumbs': 0, 'right_min': 0,
    }

    TIP_IDS = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}
    PIP_IDS = {'thumb': 3, 'index': 6, 'middle': 10, 'ring': 14, 'pinky': 18}

    def detect_gesture(landmarks):
        def is_finger_up(name):
            tip = landmarks[TIP_IDS[name]]
            pip = landmarks[PIP_IDS[name]]
            return tip.y < pip.y

        index_up = is_finger_up('index')
        middle_up = is_finger_up('middle')
        ring_up = is_finger_up('ring')
        pinky_up = is_finger_up('pinky')
        thumb_up = is_finger_up('thumb')

        if index_up and middle_up and not (ring_up or pinky_up or thumb_up):
            return 'one'
        if index_up and middle_up and ring_up and not (thumb_up):
            return 'min'
        if thumb_up and not (index_up or middle_up or ring_up or pinky_up):
            return 'thumbs'
        return None

    tic = time.time()

    TARGET_FPS = 30
    FRAME_INTERVAL = 1.0 / TARGET_FPS
    last_time = time.perf_counter()

    while True:
        left_score = right_score = 0
        ok, frame = camera.read()
        if not ok:
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        frame_gestures = {'left': None, 'right': None}
        if results.multi_hand_landmarks:
            hands_by_side = {'left': [], 'right': []}
            for idx, lm in enumerate(results.multi_hand_landmarks):
                mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
                xs = [p.x for p in lm.landmark]
                avg_x = sum(xs) / len(xs)
                side = 'left' if avg_x < 0.5 else 'right'
                gesture = detect_gesture(lm.landmark)
                hands_by_side[side].append({'gesture': gesture})
                non_none = [c for c in hands_by_side[side] if c['gesture']]
                if non_none:
                    frame_gestures[side] = non_none[-1]['gesture']

        # Atualiza contadores
        for side in ('left', 'right'):
            one_key, thumbs_key, min_key = f'{side}_one', f'{side}_thumbs', f'{side}_min'
            if frame_gestures.get(side) == 'one':
                counts[one_key] += 1
            else:
                counts[one_key] = 0

            if frame_gestures.get(side) == 'min':
                counts[min_key] += 1
            else:
                counts[min_key] = 0

            if frame_gestures.get(side) == 'thumbs':
                counts[thumbs_key] += 1
            else:
                counts[thumbs_key] = 0

        now = time.time()
        for side in ('left', 'right'):
            if counts[f'{side}_one'] >= HOLD_FRAMES:
                if (now - last_score_time) > COOLDOWN and proposal['side'] is None:
                    proposal['side'] = side
                    proposal['time'] = now
                    proposal['gesture'] = 'one'
                    counts[f'{side}_one'] = 0
            elif counts[f'{side}_min'] >= HOLD_FRAMES:
                if (now - last_score_time) > COOLDOWN and proposal['side'] is None:
                    proposal['side'] = side
                    proposal['time'] = now
                    proposal['gesture'] = 'min'
                    counts[f'{side}_min'] = 0

        if proposal['side']:
            other = 'right' if proposal['side'] == 'left' else 'left'
            if now - proposal['time'] > PROPOSAL_TIMEOUT:
                proposal['side'] = None
                proposal['gesture'] = None
            elif counts[f'{other}_thumbs'] >= HOLD_FRAMES:
                # Aplicar incremento ou decremento baseado no gesto da proposta
                if proposal['gesture'] == 'one':
                    # Incremento (+1)
                    if proposal['side'] == 'left':
                        left_score += 1
                    else:
                        right_score += 1
                elif proposal['gesture'] == 'min':
                    # Decremento (-1)
                    if proposal['side'] == 'left':
                        left_score -= 1
                    else:
                        right_score -= 1
                        
                last_score_time = now
                proposal['side'] = None
                proposal['gesture'] = None
                counts[f'{other}_thumbs'] = 0

        # Atualiza estado global
        with state_lock:
            state["frame"] = frame.copy()
            state["left_score"] = state["left_score"] + left_score
            state["right_score"] = state["right_score"] + right_score
            if proposal["side"]:
                gesture_msg = "+1" if proposal["gesture"] == "one" else "-1"
                state["message"] = f"Proposta {gesture_msg} de {proposal['side']}"
            else:
                state["message"] = "Em andamento"
            
        now = time.perf_counter()
        delta = now - last_time
        if delta < FRAME_INTERVAL:
            time.sleep(FRAME_INTERVAL - delta)
        last_time = now

def start_camera_thread():
    thread = threading.Thread(target=camera_loop, daemon=False)
    thread.start()

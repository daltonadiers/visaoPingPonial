import cv2
import mediapipe as mp
import time

camera = cv2.VideoCapture(0)
mpMaos = mp.solutions.hands
maos = mpMaos.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.5)
mpDesenho = mp.solutions.drawing_utils

left_score = 0
right_score = 0

proposal = {"side": None, "time": 0.0}
PROPOSAL_TIMEOUT = 3.0
COOLDOWN = 1.0
last_score_time = 0.0

HOLD_FRAMES = 6
counts = {
    'left_one': 0,
    'left_thumbs': 0,
    'right_one': 0,
    'right_thumbs': 0,
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

    # Verifica se está com os dois dedos levantados
    if index_up and middle_up and not (ring_up or pinky_up or thumb_up):
        return 'one'

    if thumb_up and not (index_up or middle_up or ring_up or pinky_up):
        return 'thumbs'

    return None

tic = time.time()

while True:
    sucesso, imagem = camera.read()
    imagem = cv2.flip(imagem, 1)
    if not sucesso:
        print("Erro ao capturar frame da câmera")
        break

    h, w, _ = imagem.shape
    imagemRGB = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    resultados = maos.process(imagemRGB)

    frame_gestures = {'left': None, 'right': None}

    if resultados.multi_hand_landmarks:
        hands_by_side = {'left': [], 'right': []}

        for idx, hand_landmarks in enumerate(resultados.multi_hand_landmarks):
            mpDesenho.draw_landmarks(imagem, hand_landmarks, mpMaos.HAND_CONNECTIONS)

            xs = [lm.x for lm in hand_landmarks.landmark]
            avg_x = sum(xs) / len(xs)
            side = 'left' if avg_x < 0.5 else 'right'

            gesture = detect_gesture(hand_landmarks.landmark)

            score = 0.0
            try:
                if resultados.multi_handedness and len(resultados.multi_handedness) > idx:
                    score = resultados.multi_handedness[idx].classification[0].score
            except Exception:
                score = 0.0

            hands_by_side[side].append({'gesture': gesture, 'score': float(score), 'avg_x': avg_x})

            candidates = hands_by_side[side]
            if candidates:
                non_none = [c for c in candidates if c['gesture'] is not None]
                if non_none:
                    chosen = max(non_none, key=lambda c: c['score'])
                else:
                    chosen = max(candidates, key=lambda c: c['score'])
                frame_gestures[side] = chosen['gesture']

    for side in ('left', 'right'):
        one_key = f'{side}_one'
        thumbs_key = f'{side}_thumbs'

        if frame_gestures.get(side) == 'one':
            counts[one_key] += 1
        else:
            counts[one_key] = 0

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
                counts[f'{side}_one'] = 0

    if proposal['side'] is not None:
        prop_side = proposal['side']
        other = 'right' if prop_side == 'left' else 'left'

        if now - proposal['time'] > PROPOSAL_TIMEOUT:
            proposal['side'] = None
        else:
            if counts[f'{other}_thumbs'] >= HOLD_FRAMES:
                if prop_side == 'left':
                    left_score += 1
                else:
                    right_score += 1
                last_score_time = now
                proposal['side'] = None
                counts[f'{other}_thumbs'] = 0

    overlay = imagem.copy()
    alpha = 0.15
    cv2.rectangle(overlay, (0, 0), (w // 2, h), (50, 50, 50), -1)
    cv2.rectangle(overlay, (w // 2, 0), (w, h), (50, 50, 50), -1)
    cv2.addWeighted(overlay, alpha, imagem, 1 - alpha, 0, imagem)

    cv2.putText(imagem, f'{left_score}', (w // 4 - 20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)
    cv2.putText(imagem, f'{right_score}', (3 * w // 4 - 20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)

    if proposal['side']:
        text = f'Proposal: {proposal["side"].upper()} - waiting confirmation'
        cv2.putText(imagem, text, (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    tac = time.time()
    dt = tac - tic
    fps = 0.0
    if dt > 1e-6:
        fps = 1.0 / dt
    tic = tac

    cv2.putText(imagem, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    cv2.imshow("Câmera", imagem)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
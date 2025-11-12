from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.state import state, state_lock, reset_event
import cv2
import time

router = APIRouter()

TARGET_FPS = 30
FRAME_INTERVAL = 1.0 / TARGET_FPS

def frame_generator():
    last_time = time.perf_counter()
    while True:
        with state_lock:
            frame = state.get("frame")

        if frame is not None:
            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
        now = time.perf_counter()
        delta = now - last_time
        if delta < FRAME_INTERVAL:
            time.sleep(FRAME_INTERVAL - delta)
        last_time = now

@router.get("/video_feed")
def video_feed():
    return StreamingResponse(frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/state")
def get_state():
    return {
        "playerA": "Jogador A",
        "playerB": "Jogador B",
        "scoreA": state["left_score"],
        "scoreB": state["right_score"],
        "message": state["message"],
    }

@router.post("/reset")
def reset_scores():
    with state_lock:
        state["left_score"] = 0
        state["right_score"] = 0
        state["message"] = "Em andamento"
    reset_event.set()
    return {"status": "ok"}
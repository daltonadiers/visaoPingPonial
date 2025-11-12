from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.camera_worker import start_camera_thread
from app.routes import router

app = FastAPI(title="PingPong Vision API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
def startup_event():
    start_camera_thread()

# comando para rodar:
# uvicorn main:app --host 0.0.0.0 --port 8000

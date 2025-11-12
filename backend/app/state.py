import threading

# Lock global para evitar concorrência entre threads
state_lock = threading.Lock()


state = {
    "left_score": 0,
    "right_score": 0,
    "message": "Em andamento",
    "frame": None,  # último frame processado (numpy array)
}

reset_event = threading.Event()
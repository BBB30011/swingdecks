VALID_TRANSITIONS = {
    "CREATED": ["PROCESSING"],
    "PROCESSING": ["COMPLETED", "RETRY", "FAILED"],
    "RETRY": ["PROCESSING", "FAILED"],
    "FAILED": ["DEAD_LETTER"],
    "COMPLETED": [],
    "DEAD_LETTER": []
}

def transition(current_state: str, new_state: str) -> bool:
    """
    Memvalidasi dan menjalankan transisi state untuk lifecycle job.
    Mengembalikan True jika valid, atau raise ValueError jika tidak valid.
    """
    if current_state not in VALID_TRANSITIONS:
        raise ValueError(f"State awal tidak dikenali: {current_state}")
        
    if new_state not in VALID_TRANSITIONS[current_state]:
        raise ValueError(f"Transisi state tidak diperbolehkan: {current_state} -> {new_state}")
        
    return True

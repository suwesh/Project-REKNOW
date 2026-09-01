# percept_gui.py
# client for wsl perception service
import requests
import os
import shutil
from PIL import Image, ImageDraw

wsl_perception_url = "http://localhost:8088/map_screen"

def map_screen(curr_screen):
    with open(curr_screen, "rb") as f:
        response = requests.post(
            wsl_perception_url,
            files={"file": f},
            timeout=60
        )
    response.raise_for_status()
    return response.json()

PREVIOUS_SCREENS_BASE = r"C:\Users\gui_qa\screen_states\previous_screens"

def save_iteration_screen(step_id, iteration_idx, outcome):
    """
    Save the current screen into previous_screens/step_<id>/
    """
    step_dir = os.path.join(PREVIOUS_SCREENS_BASE, f"step_{step_id}")
    os.makedirs(step_dir, exist_ok=True)

    src = r"screen_states\current\currentscreen.png"
    safe_outcome = (
        outcome
        .replace(" ", "_")
        .replace(":", "")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
    )

    dst = os.path.join(
        step_dir,
        f"{iteration_idx}_{safe_outcome}.png"
    )

    shutil.copy(src, dst)

def get_last_previous_screen(step_id):
    step_dir = os.path.join("screen_states", "previous_screens", f"step_{step_id}")
    if not os.path.exists(step_dir):
        return None
    files = sorted(os.listdir(step_dir))
    if not files:
        return None
    return os.path.join(step_dir, files[-1])

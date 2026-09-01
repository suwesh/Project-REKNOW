import cv2
import os
import re

# -----------------------------
# CONFIGURATION
# -----------------------------

BASE_DIR = r"C:\Users\gui_qa\screen_states\previous_screens"
OUTPUT_VIDEO = r"C:\Users\gui_qa\execution_replay.mp4"

FPS = 1.5  # slow enough to see each UI state


# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def extract_number(text):
    """Extract first integer found in a string"""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else -1


# -----------------------------
# COLLECT ORDERED FRAMES
# -----------------------------

frames = []

# Sort step folders: step_1, step_2, ...
step_dirs = sorted(
    [d for d in os.listdir(BASE_DIR) if d.startswith("step_")],
    key=extract_number
)

for step_dir in step_dirs:
    step_path = os.path.join(BASE_DIR, step_dir)

    images = sorted(
        [f for f in os.listdir(step_path) if f.lower().endswith(".png")],
        key=extract_number
    )

    for img_name in images:
        img_path = os.path.join(step_path, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print(f"⚠️ Skipping unreadable image: {img_path}")
            continue

        frames.append(img)

# -----------------------------
# CREATE VIDEO
# -----------------------------

if not frames:
    raise RuntimeError("❌ No frames found to create video")

height, width, _ = frames[0].shape

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))

for frame in frames:
    video.write(frame)

video.release()

print(f"✅ Video successfully created at:\n{OUTPUT_VIDEO}")

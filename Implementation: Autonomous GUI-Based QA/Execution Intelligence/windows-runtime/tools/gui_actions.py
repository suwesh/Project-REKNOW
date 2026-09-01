# gui_actions.py: for both input and outpus actions
import pyautogui, time

def navigate_to_salesforce_home():# not implemented in prototype
    return None

def capture_currentscreen():
    save_path = r"screen_states\current\currentscreen.png"
    screenshot = pyautogui.screenshot(save_path)
    return None

# -------------------------------
# Low-level primitives
# -------------------------------

def click(x: int, y: int):
    pyautogui.moveTo(x, y)
    pyautogui.click()


def type_text(text: str):
    pyautogui.typewrite(text, interval=0.03)


def press_key(key: str):
    pyautogui.press(key)


def scroll(direction: str, amount: str):
    """
    Scroll direction and magnitude.
    Positive scrolls up, negative scrolls down.
    """
    scroll_map = {
        "small": 300,
        "medium": 800,
        "large": 1500
    }

    scroll_value = scroll_map.get(amount, 300)

    if direction == "down":
        scroll_value = -scroll_value

    pyautogui.scroll(scroll_value)


# -------------------------------
# High-level executor- old- to remove after adding key press to new execute_gui_action
# -------------------------------

def execute_gui_action_old(action: dict):
    """
    Execute ONE atomic GUI action as provided by the VLM.

    Expected action schema (validated upstream):
    {
        "action": "click|type|press|scroll|ask_sahayak",
        ...
    }
    """

    if not isinstance(action, dict):
        raise ValueError(f"Action must be dict, got: {type(action)}")

    act = action.get("action")

    # ---- CLICK ----
    if act == "click":
        click(action["x"], action["y"])
        return "clicked"

    # ---- TYPE ----
    if act == "type":
        click(action["x"], action["y"])
        time.sleep(0.2)  # ensure focus
        type_text(action["text"])
        return "typed"

    # ---- KEY PRESS ----
    if act == "press":
        key = action.get("key")
        if not key:
            raise ValueError("Missing key for press action")
        press_key(key)
        return "key_pressed"

    # ---- SCROLL ----
    if act == "scroll":
        direction = action.get("direction")
        amount = action.get("amount")
        if direction not in ("up", "down"):
            raise ValueError(f"Invalid scroll direction: {direction}")
        if amount not in ("small", "medium", "large"):
            raise ValueError(f"Invalid scroll amount: {amount}")
        scroll(direction, amount)
        return "scrolled"

    # ---- ESCALATION ----
    if act == "ask_sahayak":
        # No UI action executed
        return "escalated"

    raise ValueError(f"Unknown action type: {act}")

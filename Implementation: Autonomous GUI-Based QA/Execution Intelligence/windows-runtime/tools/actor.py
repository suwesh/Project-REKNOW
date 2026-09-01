# 6 7 class 2d coordinate geometry based pure python actor
# takes ui map + agent input and resolves intent to executable action
import re, math, time
from rapidfuzz import fuzz
from tools.gui_actions import *

FUZZY_THRESHOLD = 80
def normalize_text(s):
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)   # remove punctuation
    s = re.sub(r'\s+', ' ', s)
    return s
def resolve_element(ui_map, target_text):
    # Fuzzy resolver
    # see also: https://en.wikipedia.org/wiki/Levenshtein_distance
    target_norm = normalize_text(target_text)
    # ✅ STEP 1: EXACT MATCH FIRST
    exact_matches = [
        e for e in ui_map
        if normalize_text(e["text"]) == target_norm
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        return resolve_by_geometry(exact_matches)
    # ✅ STEP 2: FUZZY ONLY IF NO EXACT MATCH
    candidates = []
    for e in ui_map:
        if e["text"] == "icon":
            continue
        elem_norm = normalize_text(e["text"])
        # symmetric fuzzy scoring
        # bidirectional>
        score1 = fuzz.token_set_ratio(target_norm, elem_norm)
        score2 = fuzz.token_set_ratio(elem_norm, target_norm)
        score = max(score1, score2)
        # ✅ Bonus for exact substring containment (human intuition)
        """if target_norm in elem_norm or elem_norm in target_norm:
            score += 10"""# removing cause of bug while clicking individual customer
        candidates.append((score, e))
    # filter by threshold
    matches = [(s, e) for s, e in candidates if s >= FUZZY_THRESHOLD]
    if not matches:
        raise RuntimeError(f"No match for '{target_text}'")
    # sort by score, descending
    matches.sort(key=lambda x: x[0], reverse=True)
    top_score = matches[0][0]
    top_candidates = [e for s, e in matches if s == top_score]
    if len(top_candidates) == 1:
        return top_candidates[0]
    # else go to geometry based tie breaker logic
    return resolve_by_geometry(top_candidates)
def resolve_by_geometry(elements):# This function exists to do what a human does subconsciously in the moment there are multiple exact text ui elements on the screen
    # rules for resolving via ui geometry
    # 1. Larger box wins->changed to smaller box wins because it was clicking on top search bar which has a bigger box
    # 2. If still tied → top-right bias (primary CTA heuristic)
    ## get largest ui element
    elements = [e for e in elements if is_likely_actionable(e)]
    elements.sort(key=lambda e: e["center"][1], reverse=True)
    elements.sort(key=get_box_area)# removed reverse=True for point 1.
    largest_area = get_box_area(elements[0])
    largest = [e for e in elements if abs(get_box_area(e) - largest_area) < 1e-3]
    if len(largest) == 1:
        return largest[0]
    ## else get top-right biased element
    max_x = max(e["center"][0] for e in largest)
    min_y = min(e["center"][1] for e in largest)
    anchor = (max_x, min_y)
    largest.sort(
        key=lambda e: (e["center"][0] - anchor[0]) ** 2 +
                        (e["center"][1] - anchor[1]) ** 2
    )
    return largest[0]
def get_box_area(e):
    x1, y1, x2, y2 = e["box"]
    return max(0, x2-x1)*max(0, y2-y1)
def is_likely_actionable(element):
    x1, y1, x2, y2 = element["box"]
    w = x2 - x1
    h = y2 - y1

    aspect_ratio = w / max(h, 1)

    # Filter out section headers / background labels
    if h < 14 and w > 200:
        return False

    # Filter ultra-wide containers
    if aspect_ratio > 15:
        return False

    return True

# -------------------------------
# High-level executor
# -------------------------------
def execute_gui_action(action: dict, ui_map: list):
    intent = action.get("intent")
    if intent == "wait":
        return "wait"
    if intent == "scroll":
        scroll(direction="down", amount="medium")
        return "scrolled"
    
    target_text = action.get("target_text")
    if not target_text:
        raise RuntimeError("Missing target_text")
    element = resolve_element(ui_map, target_text)
    cx, cy = element["center"]
    
    if intent == "click":
        click(cx, cy)
        return f"clicked '{target_text}' at coordinates: ({cx}, {cy})"
    if intent == "type":
        click(cx, cy)# focus text box before typing
        time.sleep(0.2)  # ensure focus
        type_text(action.get("type_value", ""))
        return f"typed into '{target_text}' at coordinates: ({cx}, {cy})"
    raise RuntimeError(f"Unknown intent {intent}")

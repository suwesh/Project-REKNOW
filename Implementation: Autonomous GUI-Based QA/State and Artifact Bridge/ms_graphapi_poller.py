import requests
import json
import msal
import pdfplumber
from docx import Document
import io, time, os
from ms_graph_api_auth import get_access_token, YOUR_EMAIL_ID
from ms_graph_api_utils import list_runfolder_files, fetch_changed_file
from ms_graph_api_handlers import process_automation_run_state_change

def load_tracker():
    with open("/opt/qa_root_processedruns.json") as tf:
        return json.load(tf)
def save_tracker(tracker):
    with open("/opt/qa_root_processedruns.json", "w") as f:
        json.dump(tracker, f, indent=2)

def list_run_folders():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = (
        "https://graph.microsoft.com/v1.0"
        f"/users/{YOUR_EMAIL_ID}"
        f"/drive/root:/qa_root:/children" #qa_root is the root folder where run folders are created per email recieved
    )
    res = requests.get(url, headers=headers, timeout=60)
    res.raise_for_status()
    items = res.json().get("value", [])
    # return only folders
    return [item for item in items if "folder" in item]

def poll_run_states(rag_resources):
    tracker = load_tracker()
    while True:
        # list all existing run folder under qa_root
        run_folders = list_run_folders()
        for folder in run_folders:
            run_folder = folder["name"]
            # track states per run folder
            tracker.setdefault(run_folder, [])
            try:# list run_state.json file in 06_Status child folder
                status_files = list_runfolder_files(run_folder, "06_Status")
            except Exception as e:
                continue
            for f in status_files:
                if f["name"] != "run_state.json":
                    continue
                state_data = fetch_changed_file(f["id"])
                curr_state = state_data.get("state")
                if not curr_state:
                    continue
                # if <this state> for <this folder> is already there in tracker means it was already handled -> skip
                if curr_state in tracker[run_folder]:
                    continue
                process_automation_run_state_change(run_folder, state_data, rag_resources)
                tracker[run_folder].append(curr_state)
                save_tracker(tracker)
        time.sleep(3)

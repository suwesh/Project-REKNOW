# mr_tester.py
import requests, json, time
from tools.percept_gui import *
from tools.your_domain_knowledge_retrieval import * # replace with your actual domain knowledge retrieval function
from tools.gui_actions import capture_currentscreen
from tools.operator_utils import *
from tools.actor import *
# load cnn model in wsl to infer on gpu and send req from windows

personas = load_personas()

with open('test_execution_plan.json', 'r') as sf:
    data = json.load(sf)
    steps = data['business_steps']

def execute_steps(steps):
    previous_action = "start"
    outcome = "start"
    for idx, step in enumerate(steps):
        print(f"\n▶️ Starting Step {step['step_id']}")
        attempt = 0
        step_done = False
        while not step_done:
            attempt += 1
            print(f"Attempt {attempt}")
            # 1️⃣ Capture screen
            capture_currentscreen()  # saves to current/currentscreen.png
            curr_screen_path = r"screen_states\current\currentscreen.png"
            # SAVE pre-action screen
            save_iteration_screen(
                step_id=step["step_id"],
                iteration_idx=attempt - 1,
                outcome=outcome
            )
            prev_screen_path = get_last_previous_screen(step["step_id"])
            # 2️⃣ Build UI map
            screen_map = map_screen(r"screen_states\current\currentscreen.png")
            print(f"👁️ UI Map: {screen_map}")
            # 3️⃣ Ask AGENT for next action
            agent_message = f"""Previous Action: {previous_action}\n\nCurrent Goal: {step['goal']}\n\nDecide the next UI intent."""
            action_json = to_operator(
                prev_screen_path,
                curr_screen_path,
                personas['agent'],
                agent_message
            )
            print("🧠 Agent Output:", action_json)
            # 4️⃣ call actor
            action = json.loads(action_json)
            #🦾 Execute action
            outcome = execute_gui_action(action, screen_map)
            print(f"🦾 Actor outcome: {outcome}")
            previous_action = f"{action.get('intent')} {action.get('target_text','')}"
            time.sleep(2)  # allow UI to settle
            # 5️⃣ Capture screen AFTER action
            capture_currentscreen()
            after_screen_path = r"screen_states\current\currentscreen.png"
            # 🔹 SAVE post-action screen
            save_iteration_screen(
                step_id=step["step_id"],
                iteration_idx=attempt,
                outcome=outcome
            )
            # 6️⃣ Atomic Critic
            critic_message = f"""Business Step Goal: {step['goal']}\n\nNEXT Business Step (for readiness check only):{steps[idx+1]["goal"] if idx+1 < len(steps) else "None"}\n\nLast Atomic Action:\nIntent: {action.get("intent")}\nTarget: {action.get("target_text")}\n\nEvaluate whether the current chosen action has been COMPLETED. Return DONE only if the UI both satisfies this action AND explicitly displays the UI elements required to initiate the NEXT action for the current business step, based ONLY on the current UI State."""
            critic_json = to_operator(
                prev_screen_path,
                after_screen_path,
                personas["critic"],
                critic_message
            )
            print(f"🧑‍⚖️ critic output: {critic_json}")
            critic_result = json.loads(critic_json)
            if critic_result["step_done"]:
                print(f"✅ Step action {step['step_id']} completed: {critic_result['reason']}")
                action_done = True
                break
            # 7️⃣ ASK step JUDGE
            stepjudge_message = f"""Business Step Goal: {step['goal']}\n\nNEXT Business Step (for readiness check only):{steps[idx+1]["goal"] if idx+1 < len(steps) else "None"}\n\nLast Atomic Action:\nIntent: {action.get("intent")}\nTarget: {action.get("target_text")}\n\nEvaluate whether the business step goal has been COMPLETED. Return DONE only if the UI both satisfies this step AND explicitly displays the UI elements required to initiate the NEXT business step, based ONLY on the current UI State."""
            stepjudge_json = to_operator(
                prev_screen_path,
                after_screen_path,
                personas["step_judge"],
                stepjudge_message
            )
            print(f"🧑‍⚖️ step judge output: {stepjudge_json}")
            stepjudge_result = json.loads(stepjudge_json)
            if stepjudge_result["step_done"]:
                print(f"✅ Step {step['step_id']} completed: {stepjudge_result['reason']}")
                step_done = True
                break
print("⏳ Starting Mr. Tester in 5 seconds...")
time.sleep(5)
execute_steps(steps)

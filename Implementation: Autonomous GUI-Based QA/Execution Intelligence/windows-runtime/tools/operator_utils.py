# LM Studio endpoint
"""curl http://localhost:1234/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-vl-8b",
    "system_prompt": "You answer only in rhymes.",
    "input": "What is your favorite color?"
}'"""
import json
import base64
import requests
def encode_image(path):
    with open(path, "rb") as binaryimg_file:
        return base64.b64encode(binaryimg_file.read()).decode('utf-8')
def to_operator(prev_imagepath, curr_imagepath, system_instruction, text):
    baseurl = "http://localhost:1234/api/v1/chat"
    modelid = "qwen/qwen3-vl-8b"
    input_payload = []
    # prev screen only if it exists, i.e. not None
    if prev_imagepath is not None:
        input_payload.append({
            "type": "image",
            "data_url": f"data:image/png;base64,{encode_image(prev_imagepath)}"
        })
        input_payload.append({
            "type": "text",
            "content": "Previous screen."
        })
    # current screen always exists
    input_payload.append({
            "type": "image",
            "data_url": f"data:image/png;base64,{encode_image(curr_imagepath)}"
        })
    input_payload.append({
            "type": "text",
            "content": "Current screen."
        })
    input_payload.append({
            "type": "text",
            "content": text
        })
    payload = {
        "model": modelid,
        "system_prompt": system_instruction,
        "input": input_payload,
        "store": False, # make stateless are we are controlling state and persona externally
        "temperature": 0.0,
        "top_p": 1.0,
        "max_output_tokens": 256
    }
    response = requests.post(
        baseurl,
        headers={"Content-Type": "application/json"},
        data = json.dumps(payload),
        timeout = 600
    )
    response.raise_for_status()
    data = response.json()
    return data["output"][0]["content"]

def load_personas():
    with open("personas.json", "r", encoding="utf-8") as spf:
        personas = json.load(spf)
    return personas

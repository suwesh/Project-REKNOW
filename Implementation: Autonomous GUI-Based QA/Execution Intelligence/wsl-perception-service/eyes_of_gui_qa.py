#uvicorn eyes_of_gui_qa:app --host 0.0.0.0 --port 8088
from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
#import easyocr
from PIL import Image
import numpy as np
import io, cv2, os
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import torch

app = FastAPI()

# load eyes and reader on gpu once
eyes = YOLO("/mnt/c/users/gui_qa/tools/eyes/model.pt").to('cuda')
#reader = easyocr.Reader(['en'], gpu=True)
processor = TrOCRProcessor.from_pretrained("/mnt/c/users/gui_qa/tools/tr-ocr")
model = VisionEncoderDecoderModel.from_pretrained("/mnt/c/users/gui_qa/tools/tr-ocr").to('cuda')
model.eval()

@torch.no_grad()
def trocr_read(pil_img: Image.Image) -> str:
    pixel_values = processor(
        pil_img,
        return_tensors="pt"
    ).pixel_values.to("cuda")

    generated_ids = model.generate(
        pixel_values,
        max_length=16,       # UI tokens are very short
        num_beams=1,
        do_sample=False
    )

    text = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]

    return text.strip()

@app.post("/map_screen")
async def map_screen(file: UploadFile=File(...)):
    #1. read image
    image_bytes = await file.read()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(img)
    debug_img = cv2.cvtColor(image_np.copy(), cv2.COLOR_RGB2BGR)
    #2. YOLO inference
    results = eyes.predict(
        source=image_np,
        conf=0.05,        # confidence threshold
        imgsz=1280,        # input image size
        iou=0.7,          # NMS IoU threshold
        device=0
    )
    print(f"items detected: {len(results[0])}")
    #print(results[0].orig_shape)
    #print(results[0][0])
    # Parse results
    boxes = results[0].boxes.xyxy.tolist()   # bounding boxes in [x1, y1, x2, y2]
    # Create the "UI Map" to send to Qwen
    ## crop screen shot into tiny image per bounding box to read actual text displayed for each item detected by the eyes
    ui_map = []
    h_img, w_img = image_np.shape[:2]
    PAD = 0
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box  # Coordinates from GPA
        # expand crop slightly
        cx1 = max(0, int(x1) - PAD)
        cy1 = max(0, int(y1) - PAD)
        cx2 = min(w_img, int(x2) + PAD)
        cy2 = min(h_img, int(y2) + PAD)
        # trocr based ocr now

        cropped_element = img.crop((cx1, cy1, cx2, cy2))
        #cropped_element = img.crop((x1, y1, x2, y2))
        w = cropped_element.width
        h = cropped_element.height
        if w < 8 or h < 8:
            detected_text = ""
        else: boxtext = trocr_read(cropped_element)
        # print(boxtext[0]) = [([[np.int32(9), np.int32(4)], [np.int32(83), np.int32(4)], [np.int32(83), np.int32(19)], [np.int32(9), np.int32(19)]], 'Loan Purpose', np.float64(0.5242805448982143))]
        # 3. Extract the text string
        detected_text = boxtext#" ".join([res[1] for res in boxtext]).strip()
        # ---- DEBUG DRAWING ----
        ix1, iy1 = (int(round(x1)), int(round(y1)))
        ix2, iy2 = (int(round(x2)), int(round(y2)))
        color = (0, 255, 0)  # green box
        cv2.rectangle(debug_img, (ix1, iy1), (ix2, iy2), color, 2)
        label = detected_text if detected_text else "icon"
        cv2.putText(
            debug_img,
            label,
            (ix1, max(iy1 - 5, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )
        # -----------------------
        # 4. Add to UI Map
        ui_map.append({
            "id": i,
            "text": detected_text if detected_text else "icon",## add code to identify the icon here,
            ## and change this to "element": {"type: "text", "detected_text":"<text>" if detected_text else : "element": {"type: "icon", "detected_icon":"<icon description>"
            "center": [round((x1 + x2) / 2, 2), round((y1 + y2) / 2, 2)],
            "box": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
        })
    # ✅ SAVE DEBUG IMAGE
    os.makedirs("/mnt/c/users/gui_qa/screen_states/current/detected_result", exist_ok=True)
    debug_path = f"/mnt/c/users/gui_qa/screen_states/current/detected_result/debugimg.png"
    cv2.imwrite(debug_path, debug_img)
    print(f"[DEBUG] UI map image saved at: {debug_path}")
    # Now Mr. Tester knows EXACTLY where to click for each text displayed on screen.
    print(f"items maped: {len(ui_map)}") 
    #print(ui_map[0])
    return ui_map

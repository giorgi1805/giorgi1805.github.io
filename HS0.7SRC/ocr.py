import easyocr, pyautogui
import numpy as np
from PIL import Image

# the OCR and vision was created for show, in reality, the computer use on transformer models is complete shit, expensive and slow.

def return_json(): 
    pyautogui.screenshot().save("screen.png")
    img = np.array(Image.open("screen.png"))

    reader = easyocr.Reader(['en'], gpu=True)
    result = reader.readtext(img)

    txt = []

    for bbox, text, confidence in result:
        if confidence > 0.7 and len(text.strip()) > 1:
            bbox = np.array(bbox).tolist()

            txt.append({
                "txt": text,
                "conf": round(float(confidence), 2),
                "bbox": bbox
            })

    return txt

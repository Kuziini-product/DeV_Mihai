
import pytesseract
from PIL import Image
import re
import tempfile

def extrage_dimensiuni_din_imagine(file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        img = Image.open(tmp_path)
        text = pytesseract.image_to_string(img)
        match = re.search(r"(\d{2,5})\s*[xX*]\s*(\d{2,5})\s*[xX*]\s*(\d{2,5})", text)

        if match:
            return f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
        else:
            return ""
    except Exception:
        return ""

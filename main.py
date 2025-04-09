from extractor import extract_text_from_pdf, extract_text_from_image
from formatter import format_text
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import fitz  # PyMuPDF
import google.generativeai as genai
from dotenv import load_dotenv
import io

load_dotenv()

# ==== CONFIG ====
INPUT_TYPE = "pdf"
INPUT_FILE = "roxx.pdf"
FONT_PATH = "daniel.ttf"
OUTPUT_FOLDER = "outputs"
MAX_WORDS_PER_PAGE = 200  # Limit words per page
# ================

# 🔐 Gemini Setup
genai.configure(api_key="AIzaSyCmoqEskc8m28DmDvEv2eU3ezlkbEezMs4")

def is_pdf_text_based(pdf_path):
    doc = fitz.open(pdf_path)
    for page in doc:
        if page.get_text().strip():
            return True
    return False

def extract_text_with_gemini(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    model = genai.GenerativeModel("gemini-2.0-flash")

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        img_pil = Image.open(io.BytesIO(img_bytes))
        response = model.generate_content([
            "Extract all typed text from this scanned document page.",
            img_pil
        ])
        text += response.text + "\n"

    return text

def split_text_by_words(text, max_words):
    words = text.split()
    return [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

# 🖊 Generate Handwriting Image
def generate_handwriting_image(text, output_path, font_path="daniel.ttf", font_size=32,
                               image_size=(1240, 1754), margin=100, line_spacing=10):
    font = ImageFont.truetype(font_path, font_size)
    img = Image.new("RGB", image_size, color="white")
    draw = ImageDraw.Draw(img)

    max_width = image_size[0] - 2 * margin
    max_height = image_size[1] - 2 * margin

    # Split text into lines that fit within the width
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        line_width = draw.textlength(test_line, font=font)
        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Draw lines to image
    x, y = margin, margin
    for line in lines:
        if y + font_size > image_size[1] - margin:
            break
        draw.text((x, y), line, fill="blue", font=font)
        y += font_size + line_spacing

    img.save(output_path)
    print(f"✅ Saved with margins at: {output_path}")

# 🖼 Convert JPGs to PDF
def images_to_pdf(output_folder, pdf_path="assignment_manoj.pdf", resize=True):
    image_files = sorted([
        os.path.join(output_folder, f)
        for f in os.listdir(output_folder)
        if f.endswith(".jpg")
    ])

    images = []
    for f in image_files:
        img = Image.open(f).convert('RGB')
        if resize:
            img = img.resize((1240, 1754))
        images.append(img)

    if images:
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        print(f"📄 PDF created: {pdf_path}")
    else:
        print("⚠️ No images found to convert.")

# ==== MAIN WORKFLOW ====
if INPUT_TYPE == "pdf":
    print("🔍 Checking PDF content...")
    if is_pdf_text_based(INPUT_FILE):
        print("✅ Text found in PDF.")
        raw_text = extract_text_from_pdf(INPUT_FILE)
    else:
        print("⚠️ No typed text found! Using Gemini AI for OCR...")
        raw_text = extract_text_with_gemini(INPUT_FILE)
else:
    raw_text = extract_text_from_image(INPUT_FILE)

# Format + convert to string
formatted_lines = format_text(raw_text)
if isinstance(formatted_lines, list):
    text = " ".join(
        line if isinstance(line, str) else " ".join(line)
        for line in formatted_lines
    )
else:
    text = formatted_lines

chunks = split_text_by_words(text, MAX_WORDS_PER_PAGE)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for page_num, chunk in enumerate(chunks, start=1):
    output_path = f"{OUTPUT_FOLDER}/page_{page_num}.jpg"
    generate_handwriting_image(
        text=chunk,
        output_path=output_path,
        font_path=FONT_PATH,
        image_size=(1240, 1754),  # A4 resolution
        margin=100,
        font_size=32,
        line_spacing=50
    )

print("✅ Handwritten pages saved.")
images_to_pdf(OUTPUT_FOLDER)

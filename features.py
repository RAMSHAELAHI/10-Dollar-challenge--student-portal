# features.py
import random
import datetime
from PIL import Image, ImageDraw, ImageFont  # type: ignore
import qrcode  # type: ignore
from io import BytesIO
import streamlit as st  # type: ignore

# --- Payment Gateway (Dummy - Replace with a real integration) ---
def process_payment(amount, token):
    """
    Simulates processing a payment.
    Replace this with actual payment gateway integration (e.g., Stripe, PayPal).
    """
    if not amount or not token:
        return "failure", "Invalid payment request"

    if amount <= 0:
        return "failure", "Invalid amount"

    # Simulate success/failure
    status = random.choice(["success", "failure"])
    message = "Payment successful" if status == "success" else "Payment failed"
    return status, message


# --- ID Card Generation ---
def generate_id_card(student_data):
    """Generates the student ID card image.

    Args:
        student_data (dict): Dictionary containing student information.
    """
    width, height = 800, 500

    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    font_path = "arial.ttf"
    try:
        title_font = ImageFont.truetype(font_path, 40)
        header_font = ImageFont.truetype(font_path, 24)
        text_font = ImageFont.truetype(font_path, 20)
        q3_font = ImageFont.truetype(font_path, 100)
    except Exception as e:
        st.error(f"Error loading font '{font_path}': {e}. Please place the font file in the working directory or specify a valid path.")
        # Use default font as fallback
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        q3_font = ImageFont.load_default()
        st.warning("Using default font; ID card appearance may differ.")

    blue = (0, 71, 171)
    black = (0, 0, 0)
    border_width = 5
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=blue, width=border_width)

    title_text = "GIAIC Student ID Card"
    try:
        title_width = draw.textlength(title_text, font=title_font)
    except AttributeError:
        title_width = draw.textbbox((0, 0), title_text, font=title_font)[2]
    title_x = (width - title_width) / 2
    draw.text((title_x, 20), title_text, fill=blue, font=title_font)

    logo_width, logo_height = 100, 100
    logo_x, logo_y = 50, 80
    logo_img = Image.new('RGB', (logo_width, logo_height), color=blue)
    img.paste(logo_img, (logo_x, logo_y))

    q3_text = "Q3"
    try:
        q3_bbox = draw.textbbox((0, 0), q3_text, font=q3_font)
        q3_width = q3_bbox[2] - q3_bbox[0]
        q3_height = q3_bbox[3] - q3_bbox[1]
    except Exception:
        # Fallback in case textbbox is missing or font default
        q3_width, q3_height = 100, 100

    q3_x = (width - q3_width) / 2
    q3_y = (height - q3_height) / 2

    watermark_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark_img)
    watermark_draw.text((q3_x, q3_y), q3_text, fill=(200, 200, 200, 128), font=q3_font)

    img = Image.alpha_composite(img.convert('RGBA'), watermark_img).convert('RGB')

    start_x = logo_x + logo_width + 20
    start_y = logo_y
    line_height = 30

    photo_width, photo_height = 120, 160
    photo_x = width - photo_width - 50
    photo_y = 80

    if student_data.get('photo'):
        try:
            student_photo = Image.open(BytesIO(student_data['photo']))
            student_photo = student_photo.resize((photo_width, photo_height))
            img.paste(student_photo, (photo_x, photo_y))
        except Exception as e:
            st.warning(f"Could not load student photo: {e}")
            draw.rectangle([photo_x, photo_y, photo_x + photo_width, photo_y + photo_height], outline=blue, fill=blue)
            draw.text((photo_x + 10, photo_y + 60), "Photo", fill=black, font=text_font)
    else:
        draw.rectangle([photo_x, photo_y, photo_x + photo_width, photo_y + photo_height], outline=blue, fill=blue)
        draw.text((photo_x + 10, photo_y + 60), "No Photo", fill=black, font=text_font)

    # Text fields
    fields = [
        ("Name:", 'name'),
        ("Roll No:", 'roll_no'),
        ("Email:", 'email'),
        ("Slot:", 'slot'),
        ("Contact:", 'contact'),
        ("Course:", 'course'),
        ("Teacher:", 'favorite_teacher'),
    ]

    for i, (label, key) in enumerate(fields):
        draw.text((start_x, start_y + i * line_height), label, fill=black, font=header_font)
        draw.text((start_x + 150, start_y + i * line_height), student_data.get(key, "N/A"), fill=black, font=text_font)

    qr_data = f"Name: {student_data.get('name', '')}, Roll No: {student_data.get('roll_no', '')}, Email: {student_data.get('email', '')}, Course: {student_data.get('course', '')}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=blue, back_color="white")

    qr_width, qr_height = qr_img.size
    qr_x = width - qr_width - 50
    qr_y = height - qr_height - 250
    img.paste(qr_img, (qr_x, qr_y))

    # Time in / out display
    time_in = student_data.get('time_in')
    time_out = student_data.get('time_out')
    if time_in:
        time_in_str = time_in if isinstance(time_in, str) else time_in.strftime('%Y-%m-%d %H:%M:%S')
        draw.text((50, height - 80), f"Time In: {time_in_str}", fill=black, font=text_font)
    if time_out:
        time_out_str = time_out if isinstance(time_out, str) else time_out.strftime('%Y-%m-%d %H:%M:%S')
        draw.text((50, height - 50), f"Time Out: {time_out_str}", fill=black, font=text_font)

    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

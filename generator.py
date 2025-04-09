from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_handwriting_image(
    lines,
    output_path,
    font_path,
    image_size=(1240, 1754),
    margin=100,
    font_size=32,
    line_spacing=10
):
    """
    Generates a handwriting-style image from a list of text lines.

    Args:
        lines (list): Lines of text to render.
        output_path (str): Path to save the image.
        font_path (str): Path to the handwriting font (.ttf).
        image_size (tuple): Size of the image (width, height).
        margin (int): Margin from the edges.
        font_size (int): Size of the handwriting font.
        line_spacing (int): Space between lines.

    Returns:
        list: Remaining lines not written on the page (if overflow).
    """
    img = Image.new('RGB', image_size, color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, size=font_size)

    max_width = image_size[0] - 2 * margin
    max_height = image_size[1] - 2 * margin
    line_height = font.getsize('A')[1] + line_spacing

    y = margin
    drawn_lines = []
    remaining_lines = []

    for line in lines:
        wrapped = textwrap.wrap(line, width=80)  # You can adjust width based on font_size if needed
        for wline in wrapped:
            if y + line_height > image_size[1] - margin:
                remaining_lines.append(wline)
                continue
            draw.text((margin, y), wline, fill='black', font=font)
            y += line_height
            drawn_lines.append(wline)

    img.save(output_path)
    return lines[len(drawn_lines):]

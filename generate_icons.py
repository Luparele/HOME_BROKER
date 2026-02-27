import os
from PIL import Image, ImageDraw, ImageFont

# Ensure directory exists
icon_dir = r"c:\Users\Segurança\Documents\Bolsa de valores\stocks\static\stocks\icons"
os.makedirs(icon_dir, exist_ok=True)

def create_icon(size):
    # Dark modern background
    img = Image.new('RGB', (size, size), color='#0d0f14')
    draw = ImageDraw.Draw(img)
    
    # Simple icon: blue circle with text or just a "📈" shape
    # We will draw a simple graph shape
    margin = size * 0.2
    w, h = size, size
    line_color = '#3b82f6'
    line_width = max(1, size // 15)
    
    points = [
        (margin, h - margin),
        (w * 0.4, h * 0.6),
        (w * 0.6, h * 0.7),
        (w - margin, margin)
    ]
    draw.line(points, fill=line_color, width=line_width)
    
    # Save the icon
    path = os.path.join(icon_dir, f"icon-{size}x{size}.png")
    img.save(path)
    print(f"Saved: {path}")

create_icon(192)
create_icon(512)

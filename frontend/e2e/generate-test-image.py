#!/usr/bin/env python3
"""Generate a test image for E2E tests"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple test image
width, height = 400, 400
image = Image.new('RGB', (width, height), color='lightblue')

# Draw some text
draw = ImageDraw.Draw(image)
text = "Test Image"
# Use default font
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
except:
    font = ImageFont.load_default()

# Get text bounding box
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
x = (width - text_width) / 2
y = (height - text_height) / 2

draw.text((x, y), text, fill='darkblue', font=font)

# Draw a circle
draw.ellipse([100, 100, 300, 300], outline='darkblue', width=3)

# Save the image
output_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'test-image.jpg')
image.save(output_path, 'JPEG', quality=95)

print(f"Test image created at: {output_path}")

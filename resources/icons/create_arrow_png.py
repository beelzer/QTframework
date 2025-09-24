"""Create a dropdown arrow PNG icon."""

from __future__ import annotations

from PIL import Image, ImageDraw


# Create a 12x12 image with transparent background
img = Image.new("RGBA", (12, 12), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw a filled triangle pointing down
points = [(3, 4), (9, 4), (6, 8)]
draw.polygon(points, fill=(96, 96, 96, 255))

# Save as PNG
img.save("dropdown-arrow.png")
print("Created dropdown-arrow.png")

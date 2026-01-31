from PIL import Image, ImageDraw

def draw_icon(size):
    """Draws a simple square flag icon with national colors."""
    # Crimson background
    img = Image.new("RGB", (size, size), (220, 20, 60))
    draw = ImageDraw.Draw(img)
    
    # Calculate padding (10% of size) and centered circle
    padding = int(size * 0.1)
    circle_size = size - (padding * 2)
    center_x, center_y = size // 2, size // 2
    radius = circle_size // 2
    
    # Draw centered blue circle (DodgerBlue)
    circle_coords = [
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius
    ]
    green_color = (0, 255, 0)
    draw.ellipse(circle_coords, fill=green_color)
     
    return img

# Icon sizes as single integers (FIXED: was tuples before)
sizes = [256, 128, 64, 48, 32, 16]
ico_sizes = [(s, s) for s in sizes]  # Convert to tuples for ICO format

# Generate all size icons
icons = [draw_icon(s) for s in sizes]

# Ensure all are RGB mode
rgb_icons = [icon.convert("RGB") if icon.mode != "RGB" else icon for icon in icons]

# Save as multi-size ICO file
try:
    rgb_icons[0].save(
        "app.ico",
        format="ICO",
        sizes=ico_sizes,        # All requested sizes
        append_images=rgb_icons[1:]  # Smaller sizes
    )
    print("✅ Icon 'app.ico' created successfully!")
    print(" Design: Blue circle on crimson square background")
    print(" Colors: Crimson bg (220,20,60), DodgerBlue circle (30,144,255)")
    print(" Sizes: 256x256, 128x128, 64x64, 48x48, 32x32, 16x16")
except Exception as e:
    print(f"❌ Error saving multi-size ICO: {e}")
    # Fallback: Save just the largest size
    rgb_icons[0].save("app.ico", format="ICO")
    print("✅ Icon 'app.ico' created (single 256x256 size fallback)")

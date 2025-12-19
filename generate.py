import random
import io
import zipfile
import itertools
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    font_names = ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Verdana.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except IOError:
            continue
    return ImageFont.load_default()

def generate_image_from_config(base_config):
    """Generates an image based on a specific (shape, color_name, number) tuple."""
    WIDTH, HEIGHT = 900, 500
    ROWS, COLS = 2, 3
    SHAPE_SIZE = 140
    
    SHAPES = ['rectangle', 'circle', 'triangle']
    COLORS = {'red': (255,0,0), 'yellow': (255,255,0), 'green': (0,255,0), 'blue': (0,0,255)}
    NUMBERS = [str(n) for n in range(10)]

    base_shape, base_color_name, base_num = base_config
    base_color_rgb = COLORS[base_color_name]

    # Pick the "Odd" versions (must be different from the specific base config)
    odd_shape = random.choice([s for s in SHAPES if s != base_shape])
    odd_color_name = random.choice([c for c in COLORS if c != base_color_name])
    odd_color_rgb = COLORS[odd_color_name]
    odd_num = random.choice([n for n in NUMBERS if n != base_num])

    # Pick 3 unique positions for the 3 anomalies
    indices = list(range(ROWS * COLS))
    random.shuffle(indices)
    pos_shape, pos_color, pos_num = indices[0], indices[1], indices[2]

    img = Image.new('RGB', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(img)
    font = get_font(50)

    cell_w, cell_h = WIDTH // COLS, HEIGHT // ROWS

    for i in range(ROWS * COLS):
        r, c = divmod(i, COLS)
        cx, cy = (c * cell_w) + (cell_w // 2), (r * cell_h) + (cell_h // 2)
        
        # Logic: Anomaly per slot
        curr_shape = odd_shape if i == pos_shape else base_shape
        curr_color = odd_color_rgb if i == pos_color else base_color_rgb
        curr_num   = odd_num   if i == pos_num   else base_num

        x0, y0, x1, y1 = cx - SHAPE_SIZE//2, cy - SHAPE_SIZE//2, cx + SHAPE_SIZE//2, cy + SHAPE_SIZE//2

        if curr_shape == 'rectangle':
            draw.rectangle([x0, y0, x1, y1], fill=curr_color)
        elif curr_shape == 'circle':
            draw.ellipse([x0, y0, x1, y1], fill=curr_color)
        elif curr_shape == 'triangle':
            draw.polygon([(cx, y0), (x0, y1), (x1, y1)], fill=curr_color)

        draw.text((cx, cy), curr_num, fill="black", font=font, anchor="mm", stroke_width=2, stroke_fill="white")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def generate_unique_batch_zip(n_images, zip_name="unique_shapes.zip"):
    # 1. Define all possible attributes
    SHAPES = ['rectangle', 'circle', 'triangle']
    COLOR_NAMES = ['red', 'yellow', 'green', 'blue']
    NUMBERS = [str(n) for n in range(10)]

    # 2. Generate every possible combination (Total 120)
    all_combinations = list(itertools.product(SHAPES, COLOR_NAMES, NUMBERS))
    random.shuffle(all_combinations)

    # Check if user requested more than exist
    if n_images > len(all_combinations):
        print(f"Warning: Maximum unique base combinations is {len(all_combinations)}.")
        print(f"Adjusting N from {n_images} to {len(all_combinations)}.")
        n_images = len(all_combinations)

    print(f"Generating {n_images} unique images...")
    
    with zipfile.ZipFile(zip_name, 'w') as zip_file:
        for i in range(n_images):
            # Take a unique combination from the shuffled list
            current_config = all_combinations[i]
            
            img_data = generate_image_from_config(current_config)
            
            # Name file by its attributes for easy verification
            # e.g., "img_001_circle_red_5.png"
            file_name = f"img_{i+1:03d}.png"
            zip_file.writestr(file_name, img_data)

    print(f"Done! {zip_name} created.")

# --- EXECUTION ---
# Note: Max N is 120
generate_unique_batch_zip(100, "batch_with_no_repeats.zip")

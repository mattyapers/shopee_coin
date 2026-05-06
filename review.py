import random
import re
from pathlib import Path
from dotenv import load_dotenv
import easyocr

load_dotenv()

SCREENSHOTS_DIR = Path("screenshots")
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}

# Review templates
REVIEW_TEMPLATES = [
    "Excellent {product}! Highly recommend this quality item. ⭐",
    "Love this {product}, great value for money and fast delivery!",
    "Amazing {product} with superb quality. Will buy again! 👍",
    "Fantastic {product}! Exactly as described, very satisfied.",
    "Perfect {product}, good packaging and arrived quickly. 😊",
    "Great purchase! This {product} is worth every penny.",
    "Impressed with the {product}, high quality and good service.",
    "Wonderful {product}! Better than expected, highly recommend.",
    "Satisfied with this {product}, good quality and timely delivery.",
    "Awesome {product}! Love the design and functionality. 🌟"
]


def extract_products_from_image(image_path: Path) -> list[str]:
    """Extract product names from screenshot using OCR."""
    reader = easyocr.Reader(['en'])  # Initialize reader (can be cached for performance)
    results = reader.readtext(str(image_path))
    
    # Extract all detected text
    all_text = ' '.join([text for _, text, _ in results])
    
    # Split by potential separators (commas, newlines approximated by spaces)
    # This is a simple heuristic - may need refinement
    potential_products = re.split(r'[,\n]', all_text)
    
    # Filter and clean product names
    products = []
    for prod in potential_products:
        prod = prod.strip()
        if len(prod) > 3 and not re.match(r'^\d+$', prod):  # Avoid numbers only
            products.append(prod)
    
    # Limit to reasonable number (assume max 10 products per screenshot)
    return products[:10]


def generate_review(product: str) -> str:
    """Generate a simple review using templates."""
    template = random.choice(REVIEW_TEMPLATES)
    return template.format(product=product)


def process_screenshot(path: Path) -> bool:
    txt_path = path.with_suffix(".txt")
    if txt_path.exists():
        print(f"  SKIP  {path.name} (review already exists)")
        return False

    print(f"  GEN   {path.name} ... ", end="", flush=True)

    try:
        products = extract_products_from_image(path)
        if not products:
            print("FAILED (no products detected)")
            return False
        
        items = []
        for product in products:
            review = generate_review(product)
            items.append({"name": product, "review": review})
            
    except Exception as e:
        print(f"FAILED ({e})")
        return False

    lines = []
    for i, item in enumerate(items, 1):
        lines.append(f"--- Item {i}: {item['name']} ---")
        lines.append(item["review"])
        lines.append("")

    txt_path.write_text("\n".join(lines).strip(), encoding="utf-8")
    print(f"OK ({len(items)} item{'s' if len(items) != 1 else ''})")
    return True


def main():
    if not SCREENSHOTS_DIR.exists():
        SCREENSHOTS_DIR.mkdir()
        print(f"Created {SCREENSHOTS_DIR}/ — drop your Shopee order screenshots in there, then re-run.")
        return

    screenshots = sorted([
        p for p in SCREENSHOTS_DIR.iterdir()
        if p.suffix.lower() in SUPPORTED_FORMATS
    ])

    if not screenshots:
        print(f"No screenshots found in {SCREENSHOTS_DIR}/")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        return

    print("\nShopee Review Generator (OCR-based)")
    print(f"Found {len(screenshots)} screenshot(s) in {SCREENSHOTS_DIR}/\n")

    generated = 0
    for path in screenshots:
        if process_screenshot(path):
            generated += 1

    print(f"\nDone. {generated} new review(s) generated.")
    if generated:
        print("Open the .txt files next to your screenshots to copy reviews.")
    print()


if __name__ == "__main__":
    main()

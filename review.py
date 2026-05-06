import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()

SCREENSHOTS_DIR = Path("screenshots")
QUOTA_STATE_FILE = Path(".quota_state")
DAILY_LIMIT = 1500
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg"}

PROMPT = """You are writing authentic Shopee Singapore buyer reviews for coin rewards.

Look at this Shopee order screenshot. For each visible product, write a short review.

Rules:
- Mention a specific detail from the image (product name, color, variant, packaging, etc.)
- Keep each review between 60–100 characters
- Write in English, 5-star positive tone
- Vary your phrasing — each review should sound different (different sentence structure, word choice)
- Occasionally (not always) use 1 relevant emoji
- Do NOT make up details not visible in the image

Return ONLY a JSON array, no other text:
[{"name": "product name as shown", "review": "review text here"}, ...]"""


def load_quota() -> dict:
    today = datetime.date.today().isoformat()
    if QUOTA_STATE_FILE.exists():
        data = json.loads(QUOTA_STATE_FILE.read_text())
        if data.get("date") == today:
            return data
    return {"date": today, "used": 0}


def save_quota(quota: dict) -> None:
    QUOTA_STATE_FILE.write_text(json.dumps(quota))


def warn_quota(quota: dict) -> None:
    used = quota["used"]
    remaining = DAILY_LIMIT - used
    bar = "#" * (used * 20 // DAILY_LIMIT) + "-" * ((DAILY_LIMIT - used) * 20 // DAILY_LIMIT)
    print(f"  Quota: [{bar}] {used}/{DAILY_LIMIT} used today ({remaining} remaining)")
    if remaining < 100:
        print(f"  WARNING: Only {remaining} requests left today!")


def process_screenshot(path: Path, model, quota: dict) -> bool:
    txt_path = path.with_suffix(".txt")
    if txt_path.exists():
        print(f"  SKIP  {path.name} (review already exists)")
        return False

    if quota["used"] >= DAILY_LIMIT:
        print(f"  STOP  Daily quota reached ({DAILY_LIMIT}/day). Run again tomorrow.")
        return False

    print(f"  GEN   {path.name} ... ", end="", flush=True)

    try:
        img = Image.open(path)
        response = model.generate_content([PROMPT, img])
        quota["used"] += 1
        save_quota(quota)

        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        items = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FAILED (bad JSON: {e})")
        return False
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
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set. Copy .env.example to .env and add your key.")
        print("Get a free key at: https://aistudio.google.com/app/apikey")
        return

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

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    quota = load_quota()

    print(f"\nShopee Review Generator")
    print(f"Found {len(screenshots)} screenshot(s) in {SCREENSHOTS_DIR}/\n")
    warn_quota(quota)
    print()

    generated = 0
    for path in screenshots:
        if process_screenshot(path, model, quota):
            generated += 1

    print(f"\nDone. {generated} new review(s) generated.")
    if generated:
        print(f"Open the .txt files next to your screenshots to copy reviews.")
    warn_quota(quota)
    print()


if __name__ == "__main__":
    main()

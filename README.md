# shopee-coin

Generate authentic Shopee reviews from order screenshots to farm coins.

Uses Gemini 2.0 Flash (free tier, 1500 req/day) — no cost for normal use.

## Setup

1. Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Run `setup.bat` — creates venv, installs deps, creates `.env`
3. Edit `.env` and paste your key: `GEMINI_API_KEY=your_key_here`

## Usage

1. Drop Shopee order screenshots (PNG/JPG) into `screenshots/`
2. Double-click `run.bat`
3. Each screenshot gets a `.txt` sidecar with the generated review(s)
4. Copy-paste into Shopee and set your star rating manually

Re-running is safe — already-processed screenshots are skipped.

## Notes

- Screenshots and `.txt` files are gitignored and never committed
- Multi-item orders: one `.txt` with numbered sections per product
- Quota usage is printed each run; resets daily at midnight

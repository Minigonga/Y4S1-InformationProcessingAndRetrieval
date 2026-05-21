import csv
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

csv_file = BASE_DIR.parent / "games_cleaned.csv"
json_file = BASE_DIR.parent / "games_cleaned.json"

# --------------------------
# Helper functions
# --------------------------

def split_to_list(value):
    """Split a comma-separated string into a clean list."""
    if not value or value.strip() == "":
        return []
    return [v.strip() for v in value.split(',') if v.strip()]

def to_int(value):
    """Convert safely to integer."""
    try:
        return int(float(value))
    except:
        return 0

def to_float(value):
    """Convert safely to float."""
    try:
        return float(value)
    except:
        return 0.0

def to_bool(value):
    """Convert Windows/Mac/Linux columns to booleans ('True'/'False' or '1'/'0')."""
    if isinstance(value, str):
        value = value.strip().lower()
        return value in ["true", "1", "yes", "y"]
    return bool(value)

def parse_date(value):
    """Convert date strings to ISO 8601 (YYYY-MM-DD)."""
    if not value:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except:
            pass
    return ""

# --------------------------
# Processing
# --------------------------

data = []

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    for idx, row in enumerate(reader, start=1):

        # Parse Achievements list
        raw_achievements = split_to_list(row.get("Achievements", ""))
        achievements_list = []
        for a in raw_achievements:
            try:
                achievements_list.append(int(a))
            except:
                pass

        doc = {
            "id": idx,

            # Core fields    
            "title": row.get("Name", ""),
            "release_date": parse_date(row.get("Release date", "")),
            "estimated_owners": split_to_list(row.get("Estimated owners", "")),
            "peak_CCU": to_int(row.get("Peak CCU", 0)),
            "required_age": to_int(row.get("Required age", 0)),
            "price": to_float(row.get("Price", 0)),
            "DLC_count": to_int(row.get("DLC count", 0)),

            # Text content
            "about_the_game": row.get("About the game", ""),

            # Language fields
            "supported_languages": split_to_list(row.get("Supported languages", "")),
            "full_audio_languages": split_to_list(row.get("Full audio languages", "")),

            # Reviews
            "reviews": row.get("Reviews", ""),
            "positive": to_int(row.get("Positive", 0)),
            "negative": to_int(row.get("Negative", 0)),

            # Platforms
            "windows": to_bool(row.get("Windows", "")),
            "mac": to_bool(row.get("Mac", "")),
            "linux": to_bool(row.get("Linux", "")),

            # Extra metadata
            "metacritic_score": to_int(row.get("Metacritic score", 0)),
            "achievements": achievements_list,
            "notes": row.get("Notes", ""),

            # Playtime
            "average_playtime_forever": to_int(row.get("Average playtime forever", 0)),
            "median_playtime_forever": to_int(row.get("Median playtime forever", 0)),

            # Entities
            "developers": split_to_list(row.get("Developers", "")),
            "publishers": split_to_list(row.get("Publishers", "")),

            # Multi-valued classification fields
            "categories": split_to_list(row.get("Categories", "")),
            "genres": split_to_list(row.get("Genres", "")),
            "tags": split_to_list(row.get("Tags", "")),
            "header_image": row.get("Header image", "")
        }

        data.append(doc)

# Write JSON output
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Converted {len(data)} games from CSV to JSON at {json_file}")

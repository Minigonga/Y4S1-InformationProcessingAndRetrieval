import json
from datetime import datetime
from pathlib import Path

def age_label(required_age):
    labels = []
    try:
        a = int(float(required_age))
    except Exception:
        a = 0

    if a == 0:
        return["All Ages", "Kids", "Teen", "Mature", "Adult"]
    if a < 13:
        return["All Ages", "Kids"]
    elif a < 17:
        return["All Ages", "Teen"]
    elif a < 18:
        return["All Ages", "Mature"]
    else:
        return["All Ages", "Adult"]


def release_year_label(release_date):
    if not release_date:
        return "Unknown"
    year = None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y"):
        try:
            year = datetime.strptime(str(release_date).split("T")[0], fmt).year
            break
        except Exception:
            continue
    if year is None:
        return "Unknown"
    if 2000 <= year <= 2010:
        return "Old"
    elif 2011 <= year <= 2015:
        return "Moderately Old"
    elif 2016 <= year <= 2020:
        return "Recent"
    elif 2021 <= year <= 2025:
        return "Very Recent"

def price_label(price):
    try:
        p = float(price)
    except Exception:
        return "Unknown"
    if p == 0:
        return "Free"
    elif p < 10:
        return "Cheap"
    elif p <= 25:
        return "Affordable"
    else:
        return "Expensive"

def os_label(game):

    windows = bool(game.get("windows", False))
    mac = bool(game.get("mac", False))
    linux = bool(game.get("linux", False))

    supported = []
    if windows:
        supported.append("Windows")
    if mac:
        supported.append("Mac")
    if linux:
        supported.append("Linux")

    return supported

def playtime_label(avg_playtime):
    try:
        h = float(avg_playtime)
    except Exception:
        return "Unknown"
    if h < 10:
        return "Casual"
    elif h <= 50:
        return "Moderate"
    else:
        return "Hardcore"

def transform_json(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        games = json.load(f)

    for game in games:
        game["age_rating_label"] = age_label(game.get("required_age", 0))
        game["release_year_label"] = release_year_label(game.get("release_date", ""))
        game["price_range_label"] = price_label(game.get("price", 0))
        game["OS_label"] = os_label(game)
        game["playtime_label"] = playtime_label(game.get("average_playtime_forever", 0))

        for field in ("windows", "mac", "linux"):
                game.pop(field, None)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    transform_json(
        "../games_cleaned.json",
        "../games.json"
    )

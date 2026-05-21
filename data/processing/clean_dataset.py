import pandas as pd
from datetime import datetime
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

input_csv = BASE_DIR.parent / "dataset.csv"
output_csv = BASE_DIR.parent / "games_cleaned.csv"

df = pd.read_csv(input_csv)

# --------------------------
# Step 1: Filtering
# --------------------------

# Keep games with long descriptions
df = df[df['About the game'].str.split().str.len() > 100]

# Keep games released in the last 25 years
current_year = datetime.now().year
df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')
df = df[df['Release date'].dt.year >= (current_year - 25)]

# Keep games with required fields
required_fields = ['Categories', 'Tags', 'Genres']
for field in required_fields:
    df = df[df[field].notna() & (df[field].str.strip() != '')]

# Sort by Peak CCU and remove duplicates
df = df.sort_values('Peak CCU', ascending=False)
df = df.drop_duplicates(subset=['Name'], keep='first')

# --------------------------
# Step 2: Drop irrelevant columns
# --------------------------
columns_to_drop = [
    'AppID', 'Website', 'Support url', 'Support email', 'Metacritic url',
    'Score rank', 'User score', 'Recommendations', 'Discount',
    'Average playtime two weeks', 'Median playtime two weeks', 'Screenshots', 'Movies'
]

df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# --------------------------
# Step 4: Change data for better readability
# --------------------------

df['Full audio languages'] = df['Full audio languages'].astype(str).str.replace(r"[\[\]']", "", regex=True)
df['Supported languages'] = df['Supported languages'].astype(str).str.replace(r"[\[\]']", "", regex=True)

# --------------------------
# Step 5: Random sampling
# --------------------------
sample_size = min(20000, len(df))
df_sampled = df.sample(n=sample_size, random_state=21)

# --------------------------
# Step 6: Save filtered dataset
# --------------------------
df_sampled.to_csv(output_csv, index=False)

print(f"Filtered dataset with {sample_size} rows saved to {output_csv}.")

"""
Data loading utilities for Ben's Accessible Menu.
Handles loading Excel files and JSON data for shows, communication phrases, etc.
"""

import os
import json
import pandas as pd
from collections import defaultdict
from core.config import DATA_DIR, LAST_WATCHED_FILE


def load_last_watched():
    """Load the last_watched.json data."""
    if os.path.exists(LAST_WATCHED_FILE):
        with open(LAST_WATCHED_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_last_watched(data):
    """Save the last_watched data to the file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LAST_WATCHED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_links(file_path="shows.xlsx"):
    """
    Reads links data from an Excel file and organizes it by type and genre.
    The Excel file should have columns such as:
      - type
      - genre
      - title
      - url
    Returns a nested defaultdict structure.
    """
    # Construct the absolute file path if needed.
    abs_path = os.path.join(DATA_DIR, file_path)
    
    try:
        # Read the Excel file into a DataFrame.
        df = pd.read_excel(abs_path)
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        return {}

    # Convert the DataFrame to a list of dictionaries.
    links = df.to_dict(orient="records")
    
    # Organize the data by type and genre.
    organized = defaultdict(lambda: defaultdict(list))
    for entry in links:
        t = entry.get("type", "misc").lower()
        genre = entry.get("genre", "misc").lower()
        organized[t][genre].append(entry)
        
    # Sort the entries within each type/genre by title.
    for t in organized:
        for genre in organized[t]:
            organized[t][genre].sort(key=lambda e: e.get("title", ""))
    
    return organized


def load_communication_phrases(file_path="communication.xlsx"):
    """
    Loads phrases from communication.xlsx in the format:
    | Category | Display | Text to Speech |
    Returns a dict: { "Category1": [(label1, speak1), (label2, speak2), ...], ... }
    """
    abs_path = os.path.join(DATA_DIR, file_path)
    try:
        df = pd.read_excel(abs_path)
    except Exception as e:
        print(f"[ERROR] Failed to load communication.xlsx: {e}")
        return {}

    phrases_by_category = defaultdict(list)
    for _, row in df.iterrows():
        category = str(row["Category"]).strip()
        label = str(row["Display"]).strip()
        speak_text = str(row["Text to Speech"]).strip()
        if category and label and speak_text:
            phrases_by_category[category].append((label, speak_text))
    return phrases_by_category
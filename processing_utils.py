import csv
import io
import logging
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TextEntry:
    text: str
    x: float
    y: float


def process_csv_bytes(csv_bytes: bytes) -> List[TextEntry]:
    """Parse CSV into a list of TextEntry objects."""
    entries: List[TextEntry] = []

    try:
        decoded = csv_bytes.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(decoded))
        
        try:
            first_row = next(reader)
        except StopIteration:
            logging.warning("Empty CSV received.")
            return entries

        header = [col.strip().lower() for col in first_row]
        has_header = header[:3] == ["text", "x", "y"]

        if not has_header:
            process_csv_row(first_row, entries)

        for row in reader:
            process_csv_row(row, entries)
            
        logging.info("Successfully parsed CSV entries")
        
    except Exception as error:
        logging.exception(f"Failed to parse CSV: {error}")
        return []

    return entries


def process_csv_row(row: list, entries: List[TextEntry]) -> None:
    """Helper to safely add entries from a CSV row."""
    if len(row) < 3:
        return
        
    text = row[0].strip()
    x_raw = row[1].strip()
    y_raw = row[2].strip()
    
    if not text or not x_raw or not y_raw:
        return
        
    try:
        x = float(x_raw)
        y = float(y_raw)
        entries.append(TextEntry(text=text, x=x, y=y))
    except ValueError:
        return


def group_horizontally(entries: List[TextEntry]) -> List[Dict[str, Any]]:
    """Group entries into horizontal lines based on Y coordinate."""
    groups_dict = {}
    for entry in entries:
        y_key = int(entry.y)
        if y_key not in groups_dict:
            groups_dict[y_key] = {"y": y_key, "texts": []}
        groups_dict[y_key]["texts"].append(entry.text)
    
    groups = sorted(groups_dict.values(), key=lambda g: g["y"])
    return groups


def group_vertically(entries: List[TextEntry]) -> List[Dict[str, Any]]:
    """Group entries into vertical columns based on X coordinate."""
    groups_dict = {}
    for entry in entries:
        x_key = int(entry.x)
        if x_key not in groups_dict:
            groups_dict[x_key] = {"x": x_key, "texts": []}
        groups_dict[x_key]["texts"].append(entry.text)
    
    groups = sorted(groups_dict.values(), key=lambda g: g["x"])
    return groups



def build_grouping_result(entries: List[TextEntry]) -> Dict[str, Any]:
    """Build the final JSON result structure."""
    horizontal = group_horizontally(entries)
    vertical = group_vertically(entries)

    return {
        "horizontal_groups": horizontal,
        "vertical_groups": vertical,
    }
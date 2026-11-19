"""Foundation content imported from the original TypeScript data files."""
import json
from pathlib import Path

_content = json.loads(Path(__file__).with_name("legacy_content.json").read_text(encoding="utf-8"))
CHAPTERS = _content["journey"] + _content["professional"]
INITIATIVES = _content["initiatives"]
FOCUS_AREAS = [tuple(area) for area in _content["focus_areas"]]
CONTACTS = [
    {"name": "The Foundation", "role": "Foundation Contact", "email": "cheisthakochhar.foundation@gmail.com", "phone": "8826348181"},
    {"name": "Lt Gen Dr S P Kochhar", "role": "Cheistha’s Father", "email": "kochharsp@yahoo.com", "phone": "9871554400"},
]
GALLERIES = [
    {"slug": "early-childhood", "title": "Early Childhood"},
    {"slug": "primary-school", "title": "Primary School"},
    {"slug": "school-years", "title": "School Years"},
    {"slug": "college", "title": "College"},
    {"slug": "centre-for-civil-society", "title": "Centre for Civil Society"},
    {"slug": "uidai", "title": "UIDAI"},
    {"slug": "mckinsey", "title": "McKinsey & Company"},
    {"slug": "young-india-fellowship", "title": "Young India Fellowship"},
    {"slug": "planning-commission", "title": "Planning Commission"},
    {"slug": "university-of-chicago", "title": "University of Chicago"},
    {"slug": "niti-aayog", "title": "NITI Aayog"},
    {"slug": "london-school-of-economics", "title": "London School of Economics"},
]

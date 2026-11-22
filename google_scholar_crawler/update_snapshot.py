"""Copy fresh citation counts from results/gs_data.json into the site's _data files.

Only the numbers change; comments and formatting in the YAML are left alone.
Run from the repository root:  python google_scholar_crawler/update_snapshot.py
"""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
data = json.loads((root / "google_scholar_crawler/results/gs_data.json").read_text())
pubs = data["publications"]

academic = root / "_data/academic.yml"
text = academic.read_text()

def replace_count(match):
    pub = pubs.get(match.group(2))
    return match.group(1) + str(pub["num_citations"]) if pub else match.group(0)

text = re.sub(r'(scholar_id: "([^"]+)"\n\s+citations: )(\d+)', replace_count, text)
academic.write_text(text)

profile = root / "_data/profile.yml"
profile.write_text(re.sub(r"(citations_fallback: )\d+", rf"\g<1>{data['citedby']}", profile.read_text()))

print(f"Snapshot updated: {data['citedby']} total citations")

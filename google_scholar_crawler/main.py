"""Fetch Google Scholar profile data and write it to results/.

results/gs_data.json          full profile, read live by the homepage
results/gs_data_shieldsio.json  total citations in shields.io endpoint format
"""
import json
import os
import sys
from datetime import datetime, timezone

from scholarly import scholarly

author = scholarly.search_author_id(os.environ["GOOGLE_SCHOLAR_ID"])
scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])

# Google sometimes serves a captcha page instead of data. Fail loudly rather
# than overwrite good numbers with empty ones.
if not author.get("citedby") or not author.get("publications"):
    sys.exit("Scholar returned no citation data (possibly rate-limited); keeping previous data.")

author["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
author["publications"] = {p["author_pub_id"]: p for p in author["publications"]}

os.makedirs("results", exist_ok=True)
with open("results/gs_data.json", "w") as f:
    json.dump(author, f, ensure_ascii=False)
with open("results/gs_data_shieldsio.json", "w") as f:
    json.dump({"schemaVersion": 1, "label": "citations", "message": str(author["citedby"])}, f)

print(f"{author['name']}: {author['citedby']} citations across {len(author['publications'])} items")

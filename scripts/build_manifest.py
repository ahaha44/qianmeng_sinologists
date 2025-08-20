import os, sys, json
from bs4 import BeautifulSoup


def extract_name(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
        if title.endswith(" - Wikipedia"):
            title = title[:-len(" - Wikipedia")]
        return title or os.path.basename(path)
    except Exception:
        return os.path.basename(path)

if __name__ == "__main__":
    people_dir = sys.argv[1]
    out_path = sys.argv[2]
    items = []
    for name in sorted(os.listdir(people_dir)):
        if name.lower().endswith(".html"):
            items.append({
                "name": extract_name(os.path.join(people_dir, name)),
                "file": name
            })
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

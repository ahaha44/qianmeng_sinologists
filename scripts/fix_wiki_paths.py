import os, sys
from bs4 import BeautifulSoup

WIKI = "https://en.wikipedia.org"

def absolutize(url: str) -> str:
    if not url:
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return WIKI + url
    return url

def process_file(src_path, dst_path):
    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        for attr in ("href","src"):
            if tag.has_attr(attr):
                tag[attr] = absolutize(tag[attr])
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]
    os.makedirs(dst_dir, exist_ok=True)
    for name in os.listdir(src_dir):
        if name.lower().endswith(".html"):
            process_file(os.path.join(src_dir, name), os.path.join(dst_dir, name))

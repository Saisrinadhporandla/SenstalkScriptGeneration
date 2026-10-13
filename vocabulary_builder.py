import json
import requests
from bs4 import BeautifulSoup

BASE = "https://docs.eggplantsoftware.com/epf"

PAGES = {
    "commands": "epf-qr-eggplant-commands",
    "functions": "epf-qr-eggplant-functions",
}


def page_url(slug, version):
    if version == "latest":
        return f"{BASE}/{slug}/"
    return f"{BASE}/{version}/{slug}/"


def split_names(cell_text):
    text = cell_text.replace("/", ",").replace(" and ", ",")
    names = [name.strip() for name in text.split(",")]
    return [name for name in names if name]


def read_page(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    current = []
    deprecated = []
    for table in soup.find_all("table"):
        heading = table.find_previous(["h1", "h2", "h3"])
        is_deprecated = heading is not None and "deprecated" in heading.get_text().lower()

        for row in table.find_all("tr"):
            first_cell = row.find("td")
            if first_cell is None:
                continue
            names = split_names(first_cell.get_text())
            if is_deprecated:
                deprecated.extend(names)
            else:
                current.extend(names)

    return current, deprecated


def build_vocabulary(version):
    vocabulary = {
        "docs_version": version,
        "commands": [],
        "functions": [],
        "deprecated": []
    }
    for category, slug in PAGES.items():
        current, deprecated = read_page(page_url(slug, version))
        vocabulary[category] = sorted(set(current), key=str.lower)
        vocabulary["deprecated"].extend(deprecated)

    vocabulary["deprecated"] = sorted(set(vocabulary["deprecated"]), key=str.lower)
    return vocabulary


def save_vocabulary(vocabulary, path="vocabulary.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=2, ensure_ascii=False)


def first_words(script_path):
    words = set()
    with open(script_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            words.add(line.split()[0].lower())
    return words


def words_not_in_vocabulary(script_path, vocabulary):
    known = {name.lower() for name in vocabulary["commands"] + vocabulary["functions"]}
    return sorted(first_words(script_path) - known)

if __name__ == "__main__":
    vocabulary = build_vocabulary("latest")
    save_vocabulary(vocabulary)

    print("Vocabulary saved to vocabulary.json")
    print("Commands:", len(vocabulary["commands"]))
    print("Functions:", len(vocabulary["functions"]))
    print("Deprecated:", len(vocabulary["deprecated"]))
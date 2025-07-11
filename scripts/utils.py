from rapidfuzz import fuzz
from dotenv import load_dotenv
import os
import re

load_dotenv()
sortAlphabetically = os.getenv("SORT_ALPHABETICALLY") == "true"




def write_to_file(filePath, items, ):
    if sortAlphabetically:
        items = sorted(items, key=lambda x: (x[0].lower(), x[1][0].lower()))
    with open(filePath, "w", encoding="utf-8") as file:
        for item in items:
            name = item[0]
            artists = item[1] if isinstance(item[1], str) else ", ".join(item[1])
            file.write(f"{name} - {artists}\n")


def create_folder(filePath):
    if not os.path.exists(filePath):
        os.makedirs(filePath)


def clean_name(name):
    name = name.replace("-", "").replace(",", "").strip()
    return re.sub(r"\s+", " ", name)


def should_remove(match):
    content = match.group(1).lower()
    keywords = ['remix', 'instrumental', 'version']
    return not any(keyword in content for keyword in keywords)
    

def remove_parentesis(name):
    # remove parenthesis if there is no keyword inside
    pattern = re.compile(r"\((.*?)\)")
    return pattern.sub(lambda m: "" if should_remove(m) else m.group(0), name).strip()


def are_strings_similar(string1, string2, threshold=90):
    return fuzz.ratio(string1, string2) >= threshold
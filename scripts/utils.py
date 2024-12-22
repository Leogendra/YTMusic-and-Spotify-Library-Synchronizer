import re
import os



def write_to_file(filePath, items):
    with open(filePath, "w", encoding="utf-8") as file:
        for item in items:
            file.write(f"{item[0]} - {item[1]}\n")


def create_folder(filePath):
    if not os.path.exists(filePath):
        os.makedirs(filePath)


def clean_name(name):
    pattern = re.compile(r"\((?!.*?\bremix\b).*?\)", re.IGNORECASE)
    return pattern.sub("", name).strip()
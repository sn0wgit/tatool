import os
import json
from os.path import isfile
from os.path import join

READ_ONLY:str = "r"
CREATE_FILE:str = 'w'

def compile(CURRENT_DIRECTORY:str, ARCHIVE_PATH:str, LANGUAGES:list[str]) -> None:

    directory_contents:list[str] = sorted([c for c in os.listdir(CURRENT_DIRECTORY)])

    print("Current directory:", CURRENT_DIRECTORY.replace(ARCHIVE_PATH, "")+"/")

    current_arrangement_json:dict = {"content": [], "previous_breadcrumbs": []}
    current_dictionary_example:dict = {}
    for language in LANGUAGES:
        current_dictionary_example.update({language: {}})
    current_dictionary_json:dict = {}
    for language in LANGUAGES:
        current_dictionary_json.update({language: {}})

    for content in directory_contents:

        arrangement_for_current_entry = {}

        if isfile(join(CURRENT_DIRECTORY, content)) and content.endswith(".meta"):
            current_metafile:dict = json.loads(open(join(CURRENT_DIRECTORY, content), READ_ONLY).read())

            type_from_metafile:str = current_metafile["type"]
            arrangement_for_current_entry.update({"type": type_from_metafile})

            preview_from_metafile:str = current_metafile["preview"]
            arrangement_for_current_entry.update({"preview": preview_from_metafile})

            URL_from_metafile:str = current_metafile["url"]
            arrangement_for_current_entry.update({"url": URL_from_metafile})

            namei18n_from_metafile:str = current_metafile["namei18n"]
            arrangement_for_current_entry.update({"name": namei18n_from_metafile})
            for language in current_dictionary_json.keys():
                current_dictionary_json[language][namei18n_from_metafile] = current_metafile[language+"Name"]

            current_arrangement_json["content"].append(arrangement_for_current_entry)

    if current_arrangement_json != {"content": [], "previous_breadcrumbs": []}:

        current_arrangement_file = open(join(CURRENT_DIRECTORY, "arrangement.meta.json"), CREATE_FILE)
        json.dump(current_arrangement_json, current_arrangement_file, indent=2, ensure_ascii=False)
        current_arrangement_file.close()

        print(f'"{CURRENT_DIRECTORY.replace(ARCHIVE_PATH, "")}/arrangement.meta.json" created!')

    if current_dictionary_json != current_dictionary_example:
        for language in current_dictionary_json.keys():

            current_translation_file = open(join(CURRENT_DIRECTORY, language+".meta.json"), CREATE_FILE)
            json.dump(current_dictionary_json[language], current_translation_file, indent=2, ensure_ascii=False)
            current_arrangement_file.close()

            print(f'"{CURRENT_DIRECTORY.replace(ARCHIVE_PATH, "")}/{language}.meta.json" created!')

    for directory in sorted([d for d in os.listdir(CURRENT_DIRECTORY) if os.path.isdir(join(CURRENT_DIRECTORY, d))]):
        compile(join(CURRENT_DIRECTORY, directory), ARCHIVE_PATH, LANGUAGES)

def main(LANGUAGES:list[str], ARCHIVE_PATH:str) -> None:
    """Processes `.meta` files"""

    current_directory:str = ARCHIVE_PATH

    last_directory:str = ARCHIVE_PATH
    while True:
        archive_inner_folders = sorted([d for d in os.listdir(last_directory) if os.path.isdir(join(last_directory, d))])
        if archive_inner_folders != []:
            last_directory = join(last_directory, archive_inner_folders[-1])
        else: 
            break
    print("Last directory:", last_directory)

    compile(ARCHIVE_PATH, ARCHIVE_PATH, LANGUAGES)

if __name__ == "__main__":
    print('Use "main.py"!')
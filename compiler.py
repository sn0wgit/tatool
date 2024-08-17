import os
import json
from os.path import isfile
from os.path import join

def main(LANGUAGES:list[str]) -> None:
    """Processes `.meta` files"""

    URL_PREFIX:str = "/"
    READ_ONLY:str = "r"
    CREATE_FILE:str = 'w'
    TARGET_ARCHIVE_FOLDER_NAME:str = "/GDrive original sample/items"
    ORIGIN_DIRECTORY:str = os.getcwd()+TARGET_ARCHIVE_FOLDER_NAME

    current_directory:str = os.getcwd()+TARGET_ARCHIVE_FOLDER_NAME
    directory_contents:list = sorted([c for c in os.listdir(current_directory)])

    print("Current directory:", current_directory.replace(ORIGIN_DIRECTORY, URL_PREFIX))
    print("Entry list:", directory_contents, end="\nEntry info:\n")

    current_arrangement_json:dict = {"content": [], "previous_breadcrumbs": []}
    current_dictionary_json:dict = {}
    for language in LANGUAGES:
        current_dictionary_json.update({language: {}})

    for content in directory_contents:

        arrangement_for_current_entry = {}

        if isfile(join(current_directory, content)) and content.endswith(".meta"):
            current_metafile:dict = json.loads(open(join(current_directory, content), READ_ONLY).read())

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

    print(str(current_arrangement_json)\
        .replace( "}, ",                         "},\n  " )\
        .replace( "'content': [",                "'content': [\n  " )\
        .replace( "'}],",                        "'}\n]," )\
        .replace( ", 'previous_breadcrumbs': [", ",\n'previous_breadcrumbs': [" )[1:][:-1],\
        end="\n\n"\
    )

    print("Translations: \n"+str(current_dictionary_json)\
        .replace("': {", "': {\n  ")\
        .replace("', '", "',\n  '")\
        .replace("'}, '", "'\n},\n'")\
        .replace("}}", "}\n}")\
        .replace("{'", "{\n'")\
    )

    current_arrangement_file = open(join(current_directory, "arrangement.meta.json"), CREATE_FILE)
    current_arrangement_file.write(str(current_arrangement_json).replace("'", '"').replace("False", 'false').replace("True", 'true'))
    current_arrangement_file.close()
    print('"arrangement.meta.json" created!')

    for language in current_dictionary_json.keys():
        current_translation_file = open(join(current_directory, language+".meta.json"), CREATE_FILE)
        current_translation_file.write(str(current_dictionary_json[language]).replace("'", '"'))
        current_arrangement_file.close()
        print(f'"{language}.meta.json" created!')

    """
    origin_folders = sorted([c for c in os.listdir(current_directory) if os.path.isdir(join(current_directory, c))])
    print("Folders:", origin_folders)
    for folder in origin_folders:
        print(f'Opening folder "{folder}"')
    """

if __name__ == "__main__":
    print('Use "main.py"!')
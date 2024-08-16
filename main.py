import os
import json
from os.path import isdir
from os.path import isfile
from os.path import join
"""
class Directory():
    def __init__(self, name, url):
        self.name = name
        self.files = []
        self.directories = []
        self.url = url

    def add_file(self, file):
        self.files.append(file)

    def add_directory(self, directory):
        self.directories.append(directory)

class Category(Directory):
    def __init__(self, url, name):
        super().__init__(name)
        self.type = "CATEGORY"
        self.url = url

class Item(Directory):
    def __init__(self, url, name):
        super().__init__(name)
        self.type = "ITEM"
        self.url = url

class File():
    def __init__(self, name, url):
        self.name = name
        self.type = "UNKNOWN"
        self.url = url

class PNG(File):
    def __init__(self, name, url, res):
        super().__init__(name)
        self.type = "PNG"
        self.url = url
        self.res = res

class JPG(File):
    def __init__(self, name, url, res):
        super().__init__(name)
        self.type = "JPG"
        self.url = url
        self.res = res

class SVG(File):
    def __init__(self, name, url, viewbox):
        super().__init__(name)
        self.type = "SVG"
        self.url = url
        self.viewbox = viewbox

class ThreeDS(File):
    def __init__(self, name, url):
        super().__init__(name)
        self.type = "3DS"
        self.url = url

class A3D(File):
    def __init__(self, name, url):
        super().__init__(name)
        self.type = "A3D"
        self.url = url
"""
URL_PREFIX:str = "/"
READ_ONLY:str = "r"
CREATE_FILE:str = 'w'
TARGET_ARCHIVE_FOLDER_NAME:str = "/GDrive original sample/items"
ORIGIN_DIRECTORY:str = os.getcwd()+TARGET_ARCHIVE_FOLDER_NAME

current_directory:str = os.getcwd()+TARGET_ARCHIVE_FOLDER_NAME
origin_contents:list = sorted([c for c in os.listdir(current_directory)])

print("Current directory:", current_directory.replace(ORIGIN_DIRECTORY, URL_PREFIX))
print("Entry list:", origin_contents, end="\nEntry info:\n")

current_arrangement_json:dict = {"content": [], "previous_breadcrumbs": []}
current_dictionary_json:dict = {"ru": {}, "en": {}}

for content in origin_contents:

    current_arrangement_json_content:dict = {}

    if isdir(join(current_directory, content)):
        (current_arrangement_json_content.update({"type":"ITEM"})) if (content[0].upper() == content[0]) else (current_arrangement_json_content.update({"type":"CATEGORY"}))
        current_arrangement_json_content.update({"preview":False})
        current_arrangement_json_content.update({"url":"./"+content+"/"})
        current_arrangement_json["content"].append(current_arrangement_json_content)

    if isfile(join(current_directory, content)):
        if content.endswith(".meta"):
            current_arrangement_json_content.update({"type":"META"})
            current_meta_file:dict = json.loads(open(join(current_directory, content), READ_ONLY).read())
            TYPE_FROM_META:str = current_meta_file["type"]
            NAME_FROM_META:str = current_meta_file["namei18n"]
            """Append type to content from meta"""
            for appended_content in current_arrangement_json["content"]:
                if appended_content["url"][:-1][2:] == current_meta_file["targetName"]:
                    appended_content["type"] = TYPE_FROM_META
                    appended_content["name"] = NAME_FROM_META
            for language in current_dictionary_json.keys():
                current_dictionary_json[language][NAME_FROM_META] = current_meta_file[language+"Name"]

        elif content != "arrangement.json" and content != "ru.json" and content != "en.json":
            if content.endswith(".png"):
                current_arrangement_json_content.update({"type":"PNG"})
            elif content.endswith((".jpg", ".jpeg")):
                current_arrangement_json_content.update({"type":"JPG"})
            elif content.endswith(".svg"):
                current_arrangement_json_content.update({"type":"SVG"})
            elif content.endswith(".3ds"):
                current_arrangement_json_content.update({"type":"3DS"})
            elif content.endswith(".a3d"):
                current_arrangement_json_content.update({"type":"A3D"})
            else:
                current_arrangement_json_content.update({"type":"UNKNOWN"})
                
            current_arrangement_json_content.update({"preview":"./"+content})
            current_arrangement_json_content.update({"url":"./"+content+"/"})
            current_arrangement_json["content"].append(current_arrangement_json_content)

print(str(current_arrangement_json)\
    .replace( "}, ",                         "},\n  " )\
    .replace( "'content': [",                "'content': [\n  " )\
    .replace( "'}],",                        "'}\n]," )\
    .replace( ", 'previous_breadcrumbs': [", ",\n'previous_breadcrumbs': [" )[1:][:-1],\
    end="\n\n"\
)
print("Translations: \n"+str(current_dictionary_json).replace("': {", "': {\n  ").replace("', '", "',\n  '").replace("'}, '", "'\n},\n'").replace("}}", "}\n}").replace("{'", "{\n'"))
current_arrangement_file = open(join(current_directory, "arrangement.json"), CREATE_FILE)
current_arrangement_file.write(str(current_arrangement_json).replace("'", '"').replace("False", 'false').replace("True", 'true'))
current_arrangement_file.close()
for language in current_dictionary_json.keys():
    current_translation_file = open(join(current_directory, language+".json"), CREATE_FILE)
    current_translation_file.write(str(current_dictionary_json[language]).replace("'", '"'))
    current_arrangement_file.close()
    
"""
origin_folders = sorted([c for c in os.listdir(current_directory) if os.path.isdir(join(current_directory, c))])
print(origin_folders)
"""
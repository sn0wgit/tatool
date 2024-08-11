import os
import json
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
URL_PREFIX = "/"
READ_ONLY = "r"
current_directory = "/home/user/toa-compiler/GDrive original sample/drones"
origin_contents = [c for c in os.listdir(current_directory)]
current_arrangement_json = []
#current_dictionary_json = []
print(sorted(origin_contents))
for content_index, content in enumerate(sorted(origin_contents), start=1):
    current_arrangement_json_content = {"id":content_index}
    if os.path.isdir(os.path.join(current_directory, content)):
        (current_arrangement_json_content.update({"type":"ITEM"})) if (content[0].upper() == content[0]) else (current_arrangement_json_content.update({"type":"CATEGORY"}))
        current_arrangement_json_content.update({"preview":False})
    if os.path.isfile(os.path.join(current_directory, content)):
        if content.endswith(".png"):
            current_arrangement_json_content.update({"type":"PNG"})
        elif content.endswith(".jpg") or content.endswith(".jpeg"):
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
    current_arrangement_json.append(current_arrangement_json_content)
print(str(current_arrangement_json).replace("}, ", "},\n"))
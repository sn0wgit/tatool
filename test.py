import json.tool
jsontext = """{
  "type": "explorer.folder",
  "namei18n": "drones",
  "enName": "Drones",
  "enDesc": "Game assistants",
  "ruName": "Дроны",
  "ruDesc": "Игровые помощники",
  "targetName": "drones",
  "preview": false,
  "url": "./drones/"
}"""
try:
  print(json.loads(jsontext))
except:
  print("oops")
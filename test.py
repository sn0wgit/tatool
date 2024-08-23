import json
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

print(json.loads(jsontext))
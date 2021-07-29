import json

with open('./tmp/a.json', 'r') as jf:
    jsonFile = json.load(jf)

print('Length of JSON object before cleaning: ', len(jsonFile.keys()))

testJson = {}
keyList = jsonFile.keys()
for key in keyList:
    if not key.startswith(('php')):
        print(key)
        testJson[key] = jsonFile[key]

print('Length of JSON object after cleaning: ', len(testJson.keys()))

with open('./tmp/cookiecutter.json', 'w') as jf:
    json.dump(testJson, jf, sort_keys=False, indent=4, separators=(',', ': '))

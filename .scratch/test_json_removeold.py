import json

### read json data from file
#with open('/tmp/a.json') as f:
#    data = json.load(f)

### read text from file
with open('./tmp/a.json','r') as f:
    data = f.read()

### decode JSON data
data = json.loads(data)

print('- check before:')
data['tabs'][0]['views'][1]['screenshots']

print('- Now we\'re going to overwrite the whole frame with "screenshots" for one, the first one that\'s already there. So there will only be the first record, i.e. "Screenshot URL 1" as you like.')
data['tabs'][0]['views'][1]['screenshots']  =  data['tabs'][0]['views'][1]['screenshots'][0]

print('- check after:')
data['tabs'][0]['views'][1]['screenshots']

### write encoded JSON data to output file
### warning - the tree structure will be deleted (all newlines), but the JSON format should remain original
with open('./tmp/b.json','w') as f:
    f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

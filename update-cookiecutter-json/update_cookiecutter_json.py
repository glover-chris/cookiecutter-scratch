### File used to update the cookiecutter.json with UTF-8 images and variable descriptions

import json

with open("../cookiecutter.json") as f:
    cc_template = json.load(f)

with open("header.txt", encoding="utf-8") as f:
    cc_template[" "] = f.read()

with open("../cookiecutter.json", "w") as f:
    f.write(json.dumps(cc_template, sort_keys=False, indent=4))
    f.write("\n")
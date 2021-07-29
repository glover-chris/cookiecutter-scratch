###########################################
### Python script to configure the cookiecutter.json file, based on certain user selections, which will remove json lines based on the selected options.
### then launch cookiecutter.
### Date Created: 07/15/2021
### Author: Chris Glover
### Email: chris.glover@nutanix.com

import argparse, shutil, os, distutils, json
from distutils import dir_util
import cookiecutter
import cookiecutter.main
from cookiecutter.cli import validate_extra_context

## These variables are folder paths relative to the location of this script.
DEFAULT_OUTPUT_DIR = 'launch-cookiecutter-test'
# Get the current working directory.
cwd = os.getcwd()

# Parse arguments.
def main():
    parser = argparse.ArgumentParser(description='QBiC Project Generator.', prog='generate.py', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--ipamtype', choices=['dhcp', 'static_ip', 'phpipam', 'infoblox', 'solarwinds'], required=True, default='dhcp',
        help='The type ip address management used (i.e., dhcp, static_ip, phpipam, infoblox, solarwinds).')
    parser.add_argument('--no_input', action='store_true',
        help='If set, default values, as defined in the corresponding cookiecutter.json, will be used and no prompt will be displayed. There is one cookiecutter.json file associated with each type (e.g., cli/cookiecutter.json, portal/cookiecutter.json).')
    parser.add_argument('extra_context', metavar='extra_context', nargs='*',
        help='List of variables/values that will override cookiecutter defaults (see cookiecutter documentation for a thorough explanation). Format: var1=val1 var2=val2 ... varN=valN.')
    parser.add_argument('-o', '--output-dir', default=DEFAULT_OUTPUT_DIR,
        help='Specifies the output folder of generated projects.')
    parser.add_argument('--config_file',
        help='Specifies an optional config file to override values from the default cookiecutter.json')
    args = parser.parse_args()

    args.extra_context = validate_extra_context(None, None, args.extra_context)

    generate_cookiecutter_project(args)

# Based on argument selections, reconfigure the cookiecutter.json file to remove unneeded variables.
def generate_cookiecutter_project(args):
    if "ipamtype" in args:
            ipamtype = args.ipamtype
    print('IPAM type selected is {0} \n'.format(args.ipamtype))

    with open('./cookiecutter.json', 'r') as jf:
        jsonFile = json.load(jf)

        print('Length of JSON object before cleaning: ', len(jsonFile.keys()))

    testJson = {}
    keyList = jsonFile.keys()
    for key in keyList:
        # Determine ipam solution type and configure cookiecutter.json removing unneeded variables.
        if args.ipamtype == 'dhcp':
            if not key.startswith(('php', 'infoblox', 'solarwinds')):
                print(key)
                testJson[key] = jsonFile[key]
        if args.ipamtype == 'static_ip':
            if not key.startswith(('php', 'infoblox', 'solarwinds')):
                print(key)
                testJson[key] = jsonFile[key]
        if args.ipamtype == 'phpipam':
            if not key.startswith(('infoblox', 'solarwinds')):
                print(key)
                testJson[key] = jsonFile[key]
        if args.ipamtype == 'infoblox':
            if not key.startswith(('php', 'solarwinds')):
                print(key)
                testJson[key] = jsonFile[key]
        if args.ipamtype == 'solarwinds':
            if not key.startswith(('php', 'infoblox')):
                print(key)
                testJson[key] = jsonFile[key]

    print('Length of JSON object after cleaning: ', len(testJson.keys()))

    tempfolder = "./tmp"
    if os.path.isdir(tempfolder):
        print("Temp folder exists")
    else:
        print("Temp folder does not exist.  Creating it")
        os.mkdir(tempfolder)

    with open('./tmp/cookiecutter.json', 'w') as jf:
        json.dump(testJson, jf, sort_keys=False, indent=4, separators=(',', ': '))

    os.system("cp ./tmp/cookiecutter.json ./cookiecutter.json")

    cookiecutter.main.cookiecutter(cwd, no_input=args.no_input, overwrite_if_exists=True, config_file=args.config_file, extra_context=args.extra_context, output_dir=args.output_dir)

    os.system("cp ./cookiecutter-default.json ./cookiecutter.json")

if __name__ == "__main__":
    main()
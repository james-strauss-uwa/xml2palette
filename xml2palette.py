#!/usr/bin/python

import sys
import getopt
import xml.etree.ElementTree as ET
import json


def get_filenames_from_command_line(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print("xml2palette.py -i <inputfile> -o <outputfile>")
        sys.exit(2)

    if len(opts) < 2:
        print("xml2palette.py -i <inputfile> -o <outputfile>")
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print("xml2palette.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    return inputfile, outputfile


# TODO: incomplete
def generate_uuid():
    return "9db02940-b899-4d39-9c31-d1c779bc14eb";


def create_palette_node(text, description, category, categoryType):
    return {
        "category": category,
        "categoryType": categoryType,
        "isData": False,
        "isGroup": False,
        "canHaveInputs": True,
        "canHaveOutputs": True,
        "color": "#1C2833",
        "drawOrderHint": 0,
        "key": -2,
        "text": text,
        "description": description,
        "x": 300,
        "y": 100,
        "width": 200,
        "height": 200,
        "collapsed": False,
        "showPorts": False,
        "streaming": False,
        "subject": None,
        "selected": False,
        "expanded": False,
        "inputApplicationName": "",
        "outputApplicationName": "",
        "exitApplicationName": "",
        "inputApplicationType": "Unknown",
        "outputApplicationType": "Unknown",
        "exitApplicationType": "None",
        "inputPorts": [
            {
                "Id": generate_uuid(),
                "IdText": "event"
            }
        ],
        "outputPorts": [
            {
                "Id": generate_uuid(),
                "IdText": "event"
            }
        ],
        "inputLocalPorts": [],
        "outputLocalPorts": [],
        "inputAppFields": [],
        "outputAppFields": [],
        "fields": [
            {
                "text": "Arg01",
                "name": "arg01",
                "value": "echo",
                "description": ""
            }
        ]
    }


def write_palette_json(outputfile, nodes):
    palette = {
        "modelData": {
            "fileType": "palette",
            "repoService": "GitHub",
            "repoBranch": "master",
            "repo": "ICRAR/EAGLE_test_repo",
            "filePath": outputfile,
            "sha": "",
            "git_url": ""
        },
        "nodeDataArray": nodes,
        "linkDataArray": []
    }

    with open(outputfile, 'w') as outfile:
        json.dump(palette, outfile, indent=4)


if __name__ == "__main__":
    (inputfile, outputfile) = get_filenames_from_command_line(sys.argv[1:])

    print('Input file: ' + inputfile)
    print('Output file: ' + outputfile)

    # init nodes array
    nodes = []

    # load the input xml file
    #tree = ET.parse(inputfile)
    #xml_root = tree.getroot()
    #print(xml_root.tag)

    # debug : add a sample node
    n = create_palette_node("text", "description", "DynlibApp", "Application")
    nodes.append(n)

    # write the output json file
    write_palette_json(outputfile, nodes)

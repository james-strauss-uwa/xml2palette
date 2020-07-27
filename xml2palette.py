#!/usr/bin/python

import sys
import getopt
import xml.etree.ElementTree as ET
import json
import uuid

next_key = -1

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


def get_next_key():
    global next_key

    next_key -= 1

    return next_key + 1


def create_port(name):
    return {
        "Id": str(uuid.uuid4()),
        "IdText": name
    }


def create_fields(category):
    if category == "DynlibApp":
        return [
            {
                "text": "Execution time",
                "name": "execution_time",
                "value": "5"
            }, {
                "text": "Num CPUs",
                "name": "num_cpus",
                "value": "1"
            }, {
                "text": "Group start",
                "name": "group_start",
                "value": "0"
            }, {
                "text": "Library path",
                "name": "libpath",
                "value": ""
            }]
    else:
        print("Unknown category: " + category + ". Unable to create fields.")
        return []


# NOTE: color, x, y, width, height are not specified in palette node, they will be set by the EAGLE importer
def create_palette_node(text, description, category, categoryType, inputPorts, outputPorts):
    newInputPorts = []
    newOutputPorts = []

    for inputPort in inputPorts:
        newInputPorts.append(create_port(inputPort))

    for outputPort in outputPorts:
        newOutputPorts.append(create_port(outputPort))

    return {
        "category": category,
        "categoryType": categoryType,
        "isData": False,
        "isGroup": False,
        "canHaveInputs": True,
        "canHaveOutputs": True,
        "drawOrderHint": 0,
        "key": get_next_key(),
        "text": text,
        "description": description,
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
        "inputPorts": newInputPorts,
        "outputPorts": newOutputPorts,
        "inputLocalPorts": [],
        "outputLocalPorts": [],
        "inputAppFields": [],
        "outputAppFields": [],
        "fields": create_fields(category)
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
    n0 = create_palette_node("text", "description", "DynlibApp", "Application", ["event"], ["event"])
    n1 = create_palette_node("text", "description", "DynlibApp", "Application", ["event"], ["event"])

    nodes.append(n0)
    nodes.append(n1)

    # debug
    #print("add node: " + str(n0['key']))
    #print("add node: " + str(n1['key']))

    # write the output json file
    write_palette_json(outputfile, nodes)

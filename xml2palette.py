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


def find_field_by_name(fields, name):
    for field in fields:
        if field['name'] == name:
            return field
    return None


def add_required_fields_for_category(fields, category):
    if category == "DynlibApp":
        if find_field_by_name(fields, "execution_time") is None:
            fields.append(create_field("Execution time", "execution_time", 5, ""))
        if find_field_by_name(fields, "num_cpus") is None:
            fields.append(create_field("Num CPUs", "num_cpus", 1, ""))
        if find_field_by_name(fields, "group_start") is None:
            fields.append(create_field("Group start", "group_start", 0, ""))
        if find_field_by_name(fields, "libpath") is None:
            fields.append(create_field("Library path", "libpath", "", ""))
    elif category == "PythonApp":
        if find_field_by_name(fields, "execution_time") is None:
            fields.append(create_field("Execution time", "execution_time", 5, ""))
        if find_field_by_name(fields, "num_cpus") is None:
            fields.append(create_field("Num CPUs", "num_cpus", 1, ""))
        if find_field_by_name(fields, "group_start") is None:
            fields.append(create_field("Group start", "group_start", 0, ""))
        if find_field_by_name(fields, "appclass") is None:
            fields.append(create_field("Appclass", "appclass", "test.graphsRepository", ""))

def create_field(text, name, value, description):
    return {
        "text": text,
        "name": name,
        "value": value,
        "description": description
    }


# NOTE: color, x, y, width, height are not specified in palette node, they will be set by the EAGLE importer
def create_palette_node_from_params(params):
    text = ""
    description = ""
    category = ""
    categoryType = ""
    inputPorts = []
    outputPorts = []
    inputLocalPorts = []
    outputLocalPorts = []
    fields = []

    # process the params
    for param in params:
        key = param['key']
        direction = param['direction']
        value = param['value']

        if key == "category":
            category = value
        elif key == "text":
            text = value
        elif key == "description":
            description = value
        elif key.startswith("param/"):
            # parse the param key into name, type etc
            (param, name, default_value, type) = key.split("/")
            # add a field
            fields.append(create_field(name + " (" + type + ")", name, default_value, value))
            pass
        elif key.startswith("port/") or key.startswith("local-port/"):
            # parse the port into data
            (port, name) = key.split("/")
            # add a port
            if port == "port":
                if direction == "in":
                    inputPorts.append(create_port(name))
                elif direction == "out":
                    outputPorts.append(create_port(name))
                else:
                    print("ERROR: Unknown port direction: " + direction)
            else:
                if direction == "in":
                    inputLocalPorts.append(create_port(name))
                elif direction == "out":
                    outputLocalPorts.append(create_port(name))
                else:
                    print("ERROR: Unknown local-port direction: " + direction)

    # add extra fields that must be included for the category
    add_required_fields_for_category(fields, category)

    # create and return the node
    return {
        "category": category,
        "categoryType": "Application",
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
        "inputPorts": inputPorts,
        "outputPorts": outputPorts,
        "inputLocalPorts": inputLocalPorts,
        "outputLocalPorts": outputLocalPorts,
        "inputAppFields": [],
        "outputAppFields": [],
        "fields": fields
    }


def write_palette_json(outputfile, nodes, gitrepo, version):
    palette = {
        "modelData": {
            "fileType": "palette",
            "repoService": "GitHub",
            "repoBranch": "master",
            "repo": "ICRAR/EAGLE_test_repo",
            "filePath": outputfile,
            "sha": version,
            "git_url": gitrepo
        },
        "nodeDataArray": nodes,
        "linkDataArray": []
    }

    with open(outputfile, 'w') as outfile:
        json.dump(palette, outfile, indent=4)


def process_compounddef(compounddef):
    #print("compounddef: " + compounddef.attrib['id'])
    result = []

    # get child of compounddef called "briefdescription"
    briefdescription = None
    for child in compounddef:
        if child.tag == "briefdescription":
            briefdescription = child
            break

    if briefdescription is not None:
        if len(briefdescription) > 0:
            result.append({"key":"text", "direction":None, "value":briefdescription[0].text.strip()})

    # get child of compounddef called "detaileddescription"
    detaileddescription = None
    for child in compounddef:
        if child.tag == "detaileddescription":
            detaileddescription = child
            break

    # check that detailed description was found
    if detaileddescription is None:
        #print("No detaileddescription")
        return result

    #print("detaileddescription" + str(detaileddescription))

    # search children of detaileddescription node for a para node with "simplesect" children, who have "title" children with text "EAGLE_START" and "EAGLE_END"
    para = None
    description = ""
    for ddchild in detaileddescription:
        if ddchild.tag == "para":
            if ddchild.text is not None:
                description += ddchild.text + "\n"
            for pchild in ddchild:
                if pchild.tag == "simplesect":
                    para = ddchild

    # add description
    if description != "":
        result.append({"key":"description", "direction":None, "value":description.strip()})

    # check that we found the correct para
    if para is None:
        #print("No para")
        return result

    # find parameterlist child of para
    parameterlist = None
    for pchild in para:
        #print("pchild tag " + pchild.tag)
        if pchild.tag == "parameterlist":
            parameterlist = pchild
            break

    # check that we found a parameterlist
    if parameterlist is None:
        #print("No parameterlist")
        return result

    # read the parameters from the parameter list
    for parameteritem in parameterlist:
        #print("process parameteritem")
        key = None
        direction = None
        value = None
        for pichild in parameteritem:
            if pichild.tag == "parameternamelist":
                key = pichild[0].text.strip()
                direction = pichild[0].attrib.get("direction", "").strip()
            elif pichild.tag == "parameterdescription":
                if key == "gitrepo":
                    value = pichild[0][0].text.strip()
                else:
                    value = pichild[0].text.strip()
        #print("key: " + key + " direction: " + str(direction) + " value: " + value)
        result.append({"key":key,"direction":direction,"value":value})

    return result


if __name__ == "__main__":
    (inputfile, outputfile) = get_filenames_from_command_line(sys.argv[1:])

    #print('Input file: ' + inputfile)
    #print('Output file: ' + outputfile)

    gitrepo = ""
    version = ""

    # init nodes array
    nodes = []

    # load the input xml file
    tree = ET.parse(inputfile)
    xml_root = tree.getroot()
    #print(xml_root.tag)

    for compounddef in xml_root:
        params = process_compounddef(compounddef)

        # if no params were found, or only the name and description were found, then don't bother creating a node
        if len(params) > 2:
            # print("params: " + str(params))

            # create a node
            n = create_palette_node_from_params(params)
            nodes.append(n)

        # check if gitrepo and version params were found and cache the values
        for param in params:
            key = param['key']
            value = param['value']

            if key == "gitrepo":
                gitrepo = value
            elif key == "version":
                version = value

    # debug : add a sample node
    #n0 = create_palette_node("text", "description", "DynlibApp", "Application", ["event"], ["event"])
    #n1 = create_palette_node("text", "description", "DynlibApp", "Application", ["event"], ["event"])

    #nodes.append(n0)
    #nodes.append(n1)

    # debug
    #print("add node: " + str(n0['key']))
    #print("add node: " + str(n1['key']))

    # write the output json file
    write_palette_json(outputfile, nodes, gitrepo, version)

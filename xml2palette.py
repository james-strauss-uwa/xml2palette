#!/usr/bin/python

import sys
import getopt
import xml.etree.ElementTree as ET

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

if __name__ == "__main__":
    (inputfile, outputfile) = get_filenames_from_command_line(sys.argv[1:])

    print('Input file: ' + inputfile)
    print('Output file: ' + outputfile)

    # load the input xml file
    tree = ET.parse(inputfile)
    xml_root = tree.getroot()
    print(xml_root.tag)

    # write the output json file

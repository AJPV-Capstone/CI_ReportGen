"""Test for the find_grades_file function in grades_org

Written as if this was being used in autogeneration (i.e. iterates by program that
histograms are being generated for)

Author: Ryan Letto (rmletto)
Created on: Apr. 18, 2019
Last modified: Apr. 18, 2019

"""

# Temp import for testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from grades_org import find_grades_file
from collections import namedtuple, defaultdict
import json
import logging


# logging.basicConfig(filename = 'find_grades_file_test log.log', level=logging.DEBUG)

# Proper pathing string
path = '../../Grades'

# Named tuple to store course and assessment
FileParams = namedtuple('FileParams', ['course', 'assessment'])

# Iterate across these programs for the test
programs = ['ENCM', 'ENEL', 'ENPR']

find_this_stuff = [
    # This should return 2 files from all programs
    FileParams('ENGI 1040', 'Course Grade'),
    # This should return 1 file from ECE
    FileParams('ENGI 1040', 'Circuits Grade'),
    # This should only return 1 file from ENCM
    FileParams('ENGI 6861', 'Final Exam'),
    # This should return nothing
    FileParams('ENGI 9000', 'Porridge Recipe')
]


for p in programs:
    print("GENERATING HISTOGRAMS FOR {}:\n".format(p))

    # Set up the file search hierarchy thing
    file_lists = {
        p: os.listdir(path + '/' + p),
        'Core': os.listdir(path + '/' + 'Core'),
        'ECE': os.listdir(path + '/' + 'Core')
    }

    # Iterate across the stuff-finding as if it was iteration across an indicator query
    for thing in find_this_stuff:
        # print("SEARCHING FOR GRADES DATA FOR {} {}\n".format(thing.course, thing.assessment))
        ls = defaultdict()
        for folder in file_lists.keys():
            # print("Searching for {} {} in {}".format(thing.course, thing.assessment, folder))
            ls[folder] = find_grades_file(thing.course,thing.assessment,file_lists[folder])
        
        # Use the JSON library for a pretty print
        print("DATA FOR {} {}:".format(thing.course, thing.assessment))
        print(json.dumps(ls, sort_keys=True, indent=4))
        # Add a newline for readability
        print()
        
        

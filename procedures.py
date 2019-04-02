"""PRE-SAVED REPORT GENERATION PROCEDURES"""
import pandas as pd
import os
import numpy as np
import globals
from ReportConfig import ReportConfig
from ReportGenerator import ReportGenerator
from collections import defaultdict


def separate_promo_sheet(year, grades_dir='Grades/', filename=None):
    """Separator for Engineering One promotion sheets

    Parses Engineering One promotion sheet and separates the data into different
    files. Expects to find promo sheets in current_directory/Grades/Core.

    The function can open the Excel spreadsheet in 2 ways: directly by file or
    by searching the Core folder in the grades directory for a spreadsheet that
    matches the year passed in. It will attempt to append to old grade files if
    they exist. The program has a one-time warning in place just in case the
    Grades directory gets set up improperly.

    Args:
    	year: The year that is on the spreadsheet to process. The function
            assumes that the year is one more than the academic year (i.e.
            the file called 2018-EngOneMatch.xlsx is for academic year 2017)
        grades_dir: The top folder of the grades. Used when finding file by
            year.
        filename: The file to open. Overrides opening by year
    """

    #--------------------------------------------------------------------------
    # Open promotion file
    #--------------------------------------------------------------------------

    # Open file if provided, otherwise run a search using the year
    if filename:
        print("Opening promo file", filename)
        promosheet = pd.read_excel(filename)
    else:
        print("Finding promo file using year", year)
        filename = ""
        # Get a list of files in the Core folder
        files = os.listdir(grades_dir + 'Core/')
        # Go through each file; look for the year and "EngOne"
        for file in files:
            if file.find(str(year)) != -1 and file.find('EngOne') != -1:
                filename = grades_dir + 'Core/' + file
                print ("Opening found file", filename)
                promosheet = pd.read_excel(filename)
                break

    #--------------------------------------------------------------------------
    # Grade storage setup
    #--------------------------------------------------------------------------

    print("Setting up grade dictionaries")
    # Add ENUD and Core to list of programs so that these files can be glued
    # together too
    eng_one_programs = globals.all_programs + ['ENUD','Core']
    # List of Engineering One courses to collect. These values should be
    # columns in the promotion spreadsheet, and only one column of that
    # name should exist.
    eng_one_courses = [
        'English',
        'CHEM1050',
        'MATH1001',
        'MATH2050',
        'PHYS1051',
        'ENGI1010',
        'ENGI1020',
        'ENGI1030',
        'ENGI1040'
    ]
    # Create a dictionary of programs to store grades, keyed by program and course
    master_grades = defaultdict(lambda: defaultdict())
    for p in eng_one_programs:
        for c in eng_one_courses:
            # Lists are used because they are faster than Pandas objects for
            # 1-by-1 appending
            master_grades[p][c] = list()

    #--------------------------------------------------------------------------
    # Sorting through the grades and storing them
    #--------------------------------------------------------------------------

    # Iterate over the spreadsheet by course, adding grades to their
    # respective dictionaries
    for course in eng_one_courses:
        print('\n', "Parsing course", course, '\n')
        for i, row in promosheet.iterrows():
            # temp variable to store discipline
            temp = ""
            # Determine which program the grade is associated with
            if row["Match"] == 'E':
                temp = 'ENEL'
            elif row["Match"] == 'M':
                temp = 'ENMC'
            elif row["Match"] == 'T':
                temp = 'ENCM'
            elif row["Match"] == 'C':
                temp = 'ENCV'
            elif row["Match"] == 'P':
                temp = 'ENPR'
            elif row["Match"] == 'O':
                temp = 'ONAE'
            else:
                print("No program found for row " + str(i+2) + ", adding to ENUD")
                temp = 'ENUD'

            # If the stored grade in the row is not an integer, add -1 to represent
            # no data available. Otherwise, save the row value
            if not isinstance(row[course], int):
                print ("Grade entry at row " + str(i+2) + " was not an integer. Saving as -1 to indicate NDA")
                grade_value = -1
            else:
                grade_value = row[course]

            # Add grade value to the respective course list
            master_grades[temp][course].append(grade_value)
            # If temp was not ENUD, save the grade to the 'Core' list too
            if temp != 'ENUD':
                master_grades['Core'][course].append(grade_value)


    #--------------------------------------------------------------------------
    # Grade file exporting; attempts appending
    #--------------------------------------------------------------------------
    print ("Grade loading is finished, exporting now")
    has_not_warned = True   # Safeguard for grade appending
    for p in eng_one_programs:
        for c in eng_one_courses:
            # File that the program will attempt to open
            # Example format: "Grades/ENCM/ENGI 1020 Course Grade - ENCM.xlsx"
            # English is a one-off exception which is why there's an if statement
            if c == 'English':
                file = "{}{}/{} Course Grade - {}.xlsx".format(grades_dir, p, c, p)
            else:
                file = "{}{}/{} Course Grade - {}.xlsx".format(grades_dir, p, ' '.join([c[:4],c[4:]]), p)
            try:
                print("Attempting to open", file)
                grade_sheet = pd.read_excel(file)
            except Exception as exc:
                print(exc)
                if has_not_warned:
                    has_not_warned = False  # Update has_not_warned
                    while True:
                        user_input=input("It appears that the program was unable to open a grades file in {}. The program will not append to any file of this name as a result. Continue? [y/n]".format(grades_dir))
                        if user_input == 'y':
                            print("Continuing program execution")
                            break
                        elif user_input == 'n':
                            print ("Stopping program")
                            return 0;
                        else:
                            print("You have not entered a valid input!")
                print("Creating a new file for", file)
                # Column name is the Eng One promosheet academic year
                grade_sheet = pd.DataFrame()

            # Turn the lists into Pandas Series and join them to the grade sheets
            grade_sheet = pd.concat([grade_sheet, pd.Series(master_grades[p][c], name=str(year-1))], axis=1)
            # Export as Excel file
            # English is a one-off exception which is why there's an if statement
            if c == 'English':
                file = "{}{}/{} Course Grade - {}.xlsx".format(grades_dir, p, c, p)
            else:
                file = "{}{}/{} Course Grade - {}.xlsx".format(grades_dir, p, ' '.join([c[:4],c[4:]]), p)
            print("Exporting", file)
            grade_sheet.to_excel(file, index = False)

    print("PROCEDURE COMPLETE")


def histogram_by_cohort(whitelist=None):
    """Generate histograms by cohort

    Args:
        whitelist: The same form of whitelist that gets passed to a
            ReportGenerator object
    """
    # Set up ReportConfig
    config = ReportConfig(config_file="by_cohort.json")
    # Set up ReportGenerator
    gen = ReportGenerator(config=config, whitelist=whitelist)
    # Run autogeneration
    gen.autogenerate()

    print("PROCEDURE COMPLETE")

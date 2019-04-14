"""PRE-SAVED REPORT GENERATION PROCEDURES"""
import pandas as pd
import os
import numpy as np
import globals
from ReportConfig import ReportConfig
from ReportGenerator import ReportGenerator
from collections import defaultdict
import textformatting
import logging
import datetime

# Make sure that the logs directory exists
os.makedirs('logs', exist_ok=True)
# Start a logger any time this file is imported
logging.basicConfig(filename='logs/procedures-log {}.log'.format(datetime.datetime.now()), level=logging.DEBUG)


def separate_coop_sheet(file, save_to='../Grades/'):
    """Separate co-op date into appropriate spreadsheets

    The function looks for co-op spreadsheets in "(save_to)/Co-op" and will
    split them into files by work term number and question. It initially stores
    the grades in a dictionary set up like dict[course][question][cohort] and
    converts to Pandas DataFrames during saving, as DataFrames are immutable
    and are not built to be appended to.

    Args:
        file: The name of the file to parse
        save_to: The top directory to save grades to. Defaults to saving them
            to a 'Grades' folder one directory above this one
    """
    print("Opening file {}".format(save_to + 'Co-op/' + file))
    # Open the full sheet, skipping the first row that stores indicator information
    full_sheet = pd.read_excel(save_to + 'Co-op/' + file, skiprows=1)

    # Get the year and semester from the file name
    year_and_semester = [int(s) for s in os.path.splitext(file)[0].split() if s.isdigit()][0]
    print("Obtained year and semester as {}".format(str(year_and_semester)))

    # Initialize nested defaultdicts to save the grades to.
    # Grades only saved for ENGI 001W, 002W, 003W and 004W
    # So that is hard-coded to increase parsing speed.
    print("Setting up grades dictionaries")
    grades_dict = {
        'ENGI 001W': defaultdict(lambda: defaultdict(list)),
        'ENGI 002W': defaultdict(lambda: defaultdict(list)),
        'ENGI 003W': defaultdict(lambda: defaultdict(list)),
        'ENGI 004W': defaultdict(lambda: defaultdict(list))
    }
    # Iterate across the rows of the big sheet
    print("Beginning row iteration")
    for i, row in full_sheet.iterrows():
        # Iterate across the questions (aka the column names) of the row. The
        # row is a Pandas Series, which stores the 'column names' in its
        # 'index.names' attribute as an immutable object.
        question_list = list(row.index)
        question_list.remove('Work term')
        for question in question_list:
            print("Parsing question {}".format(question))
            WT = row['Work term']   # Work term
            try:
                cohort = textformatting.get_cohort_coop(year_and_semester, WT)  # cohort
            except ValueError:
                print("Value received was not within 1-4, skipping row")
                # ValueError will occur if the work term passed in isn't from 1 to 4.
                # Skip this row if that occurs.
                continue
            # Append the question valut to the appropriate list. Example of dict call:
            # grades_dict['ENGI 001W']['Initiative']['2021'].append(row['Initiative'])
            grades_dict['ENGI 00{}W'.format(str(WT))][question][cohort].append(row[question])

    # Start exporting the things
    print("Beginning export")
    for course in grades_dict.keys():
        for question in grades_dict[course].keys():
            # Format the save name
            save_name = save_to + "Co-op/" + "{c} Employer Evaluation Form - {q} Question.xlsx".format(
                    c = course, q = question
            )
            # Try to open a grades file: it's possible that one already exists
            try:
                old_file = pd.read_excel(save_name)
                print("Found an old grades file, appending to that")
                # If this works, we have appending to do. Convert the Excel file
                # to a list-like dictionary, which is in the same format as what
                # the current grades_dict is in
                old_file = old_file.to_dict('list')
                # Run a dictionary comparison. If a key from the new dict matches
                # a key in the old file, append the two lists together. Otherwise,
                # add the new cohort entry
                for cohort in grades_dict[course][question].keys():
                    if cohort in old_file.keys():
                        print("Cohort {} already existed, appending lists".format(cohort))
                        # Strip any null values from the list
                        for x in old_file[cohort]:
                            if pd.isnull(x):
                                old_file[cohort].remove(x)
                        old_file[cohort] += grades_dict[course][question][cohort]
                    else:
                        old_file[cohort] = grades_dict[course][question][cohort]
                # Pandas requires all lists to have same length

                # Convert the old file back into a DataFrame and save it
                print("Saving file...")
                # List comprehension converts lists to Series to avoid a DataFrame
                # construction error
                df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in old_file.items() ]))
                df.to_excel(save_name, index=False)
            except FileNotFoundError:
                # Turn the question DataFrame into a dictionary, and let Pandas do its magic from there.
                # Pandas will set up the grades dictionary to have column names by cohort, just like magic
                print("Saving file...")
                df = pd.DataFrame(grades_dict[course][question])
                df.to_excel(save_name, index=False)

    print("PROCEDURE COMPLETE")

def separate_promo_sheet(year, grades_dir='../Grades/', filename=None):
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
    # Grade file exporting - apppends to files where possible
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


def histogram_by_cohort(programs=None, whitelist=None):
    """Generate histograms by cohort

    For more information, see the documentation on ReportGenerator

    Args:
        programs: The same list of programs that gets passed to a
            ReportGenerator object
        whitelist: The same form of whitelist that gets passed to a
            ReportGenerator object
    """
    # Set up ReportConfig with by_cohort configuration
    config = ReportConfig(config_file="by_cohort.json")
    # Set up ReportGenerator
    gen = ReportGenerator(config=config, whitelist=whitelist, programs=programs)
    # Run autogeneration
    gen.autogenerate()

    print("PROCEDURE COMPLETE")

"""Useful functions that should probably be methods somewhere but I dunno where to put them"""
import os
import re
import pandas as pd

def parse_row(row, instructions):
    """Turn a row of a Pandas DataFrame into a dictionary and bin list

    The data stored in the master indicator spreadsheets needs to be cleaned up
    properly for a Report to use it. This function does that.

    Args:
        row: The row of a Pandas DataFrame (so a Pandas Series) to clean up
        instructions: A comma-separated string indicating what data needs to
            be put on the header. This attribute determines the dictionary keys.
            When a dictionary key is found in multiple columns, that information
            gets glued together and separated by ' - '. One thing that this function
            does not do is fill any data for a 'Program' tag; that has to be done
            after the function call.

    Returns:
        dict: A dictionary containing the indicator information, keyed using instructions
        list(float): The bin ranges that have been converted from a comma-separated string
            to a list of floats. 0 gets appended to the front for NumPy histogram
    """
    # Handle the bins first since those are easy
    bins = [float(x) for x in row['Bins'].split(',')]

    # Convert the comma-separated string into dictionary keys
    indicator_dict = {i:"" for i in [x.strip() for x in instructions.split(',')]}

    for key in indicator_dict.keys():
        # Look for all occurrences where the key is found in the row's columns
        # and store that information in a list
        occurrences = [str(row[i]) for i in row.index if key in i]
        # Glue all collected data together with ' - ' characters
        indicator_dict[key] = ' - '.join(occurrences)

    return indicator_dict, bins


def open_grades(row, program, course_col_name = None, assessment_col_name = None, grades_top_folder = None):
    """Return a Pandas DataFrame containing grades associated to Indicator sheet row

    Args:
        row: A row from a Pandas DataFrame (so a Pandas Series)
        course_col_name: The name of the column that stores course number.
            Default is 'Course #'
        assessment_col_name: The name of the column that stores assessment.
            Default is 'Method of Assessment'
        grades_top_folder: The folder where the grade storage hierarchy starts.
            Uses os.path by default to find it

    Returns:
        pd.DataFrame: a DataFrame containing the grades
    """
    if not course_col_name:
        course_col_name = 'Course #'
    if not assessment_col_name:
        assessment_col_name = 'Method of Assessment'
    if not grades_top_folder:
        grades_top_folder = os.path.dirname(__file__) + '/Grades/'

    return pd.read_excel('{}/{}/{} {}.xlsx'.format(grades_top_folder, program, row[course_col_name], row[assessment_col_name]))


def get_cohort(x, course=None, term_taken=None):
    """Convert a year and term to equivalent cohort using course number

    Args:
        x: a number containing year and optionally, semester
            Examples: 2017, 201703, 2019
        course: The course name or number
        term_taken: An override variable for courses that have unconventional
            numbering, such as CHEM1051 being taken in term 3. Overrides any
            derivations

    Returns:
        The equivalent cohort

    Exceptions:
        NotImplementedError: If the term_taken or the first number in the course
            name is 0, that means that the course is a work term course. This
            function does not have the necessary information to determine cohort
            using just the year, semester and course number.
    """
    # Find the first number that occurs in the course UNLESS the term_taken
    # variable is used
    if not term_taken:
        term_taken = int(re.search("\d", course).group(0))

    # Convert x to a string so that it's easier to deal with
    x = str(x)
    # If term is included, split the year and semester
    if len(x) > 4:
        year = int(x[:4])
        semester = int(x[5:])
    else:
        year = int(x)
        semester = 0

    # Co-op work term check - raise error if the course found is a co-op course
    if term_taken == 0:
        raise NotImplementedError()

    # Start with cohort equalling the year. If the course was taken in the winter
    # or summer, add 1
    cohort = year
    if semester > 1:
        cohort += 1

    # Use conditionals from that point
    if term_taken in (1,2): # 20(y)01 or 20(y)02
        cohort += 5
    elif term_taken in (3,4):# 20(y+1)01 or 20(y+1)03
        cohort += 4
    elif term_taken == 5: # 20(y+2)02
        cohort += 3
    elif term_taken in (6,7):   # 20(y+3)01 or 20(y+4)03
        cohort += 2
    elif term_taken == 8: # 20(y+4)02
        cohort += 1

    return cohort

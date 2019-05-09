"""Grades organization functions

This file, along with DataStore.py, are designed to be eventually replaced by a
proper database interface. Some of the functions may be able to carry over.
"""

import pandas as pd
import numpy as np
import os
from collections import defaultdict
import logging
import textformatting as tf

def open_grades(row, program, course_col_name = None, assessment_col_name = None, grades_top_folder = None, file=None):
    """Return a Pandas DataFrame containing grades associated to Indicator sheet row

    Args:
        row: A row from a Pandas DataFrame (so a Pandas Series) that contains
            Indicator query data
        course_col_name: The name of the column that stores course number.
            Default is 'Course #'
        assessment_col_name: The name of the column that stores assessment.
            Default is 'Method of Assessment'
        grades_top_folder: The folder where the grade storage hierarchy starts.
            Uses os.path by default to find it
        file: An override variable. Pass the function the right file name, and
            it'll just open the file

    Returns:
        pd.DataFrame: a DataFrame containing the grades

    Exceptions:
        FileNotFoundError: Raises an error when the grades file cannot be opened (comes from Pandas)
    """
    if file:
        logging.debug("Attempting to open passed-in file %s", file)
        return pd.read_excel(file)
    if not course_col_name:
        course_col_name = 'Course #'
        logging.debug("Column to obtain course # in indicator sheet not specified, using %s", course_col_name)
    if not assessment_col_name:
        assessment_col_name = 'Method of Assessment'
        logging.debug("Column to obtain assessment in indicator sheet not specified, using %s", assessment_col_name)
    if not grades_top_folder:
        grades_top_folder = os.path.dirname(__file__) + '/../Grades/'
        logging.debug("Grades top folder not specified, using %s", grades_top_folder)

    file='{}/{}/{} {}.xlsx'.format(grades_top_folder, program, row[course_col_name], row[assessment_col_name])
    logging.debug("Attempting to open %s", file)
    return pd.read_excel(file)


def cols_to_cohorts(grades, course_name, course_term_offered=None):
    """Rename columns of a grades DataFrame to be cohorts

    Args:
        grades: A Pandas DataFrame with column names of either academic year or
            cohort (i.e. 201701 or 2017 as academic year notation, or 2022 as
            cohort)
        course_name: The name of the course that the grades DataFrame is for.
            Variable gets passed to get_cohort from textformatting.
        course_term_offered: The term that a course is offered. Variable gets
            passed to get_cohort function from textformatting.

    Returns:
        list(str): A list of strings, all as cohort messages
    """
    logging.info("Changing DataFrame columns to cohort messages")
    renamed_columns = list()
    for col in grades.columns:
        # Get the real size of the grade column (size without Null values)
        cohort_size = true_size(grades[col])
        renamed_columns.append("CO{}: {} STUDENTS".format(
            tf.get_cohort(col, course=course_name, term_taken = course_term_offered),
            cohort_size
        ))
    return renamed_columns


def true_size(ser):
    """Obtains the true size of a Pandas Series
    
    When getting the size of a Pandas Series, any NaN or Null entries are considered
    in the count. This becomes problematic when getting student counts because Pandas
    has to append Null values to the end of DataFrame columns when the columns are not
    the same size. As a result, all cohorts end up being the same size, even though
    that's not true. This function strips out the null values and returns the true size
    of the list. As a note, 0's are not stripped from the list; what gets stripped is
    determined by pd.isnull()

    Args:
        ser: A Pandas Series

    Returns:
        int: The size of the Pandas Series without null values
    """
    figure_out_size = list()
    # Iterate through the values of the Series
    for x in ser:
        # Append to figure_out_size as long as the value isn't Null according to Pandas
        if not pd.isnull(x):
            figure_out_size.append(x)
    
    return len(figure_out_size)


def find_grades_files(course, assessment, file_list):
    """Find grades files in a list

    This search function finds files based on the following requirements:
    1. The name starts with the Course # and assessment type
    2. The file is an Excel spreadsheet (ends with .xlsx)
    When searching, it ignores case and spacing

    Args:
        course(string): The course number to search for (i.e. 'ENGI 3891')
        assessment(string): The assessment type to search for (i.e. 'Final Exam')
        file_list(list(string)): The list of files to search

    Returns:
        A list of all file names that match the search criteria
    
    TODO:
        * Convert the matching to use regular expressions for efficiency?
    """
    matches = list()
    for file in file_list:
        bool_results = list()
        # logging.debug("Checking file %s", file)
        # Check to see if file starts with course and assessment.
        # Removes all whitespace and makes everything lowercase
        bool_results.append(
            ("".join(file.lower().split())).startswith("".join((course + assessment).lower().split()))
        )
        # logging.debug("Search for course # and assessment resulted in %s", str(bool_results[0]))
        # Check to see if file ends with .xlsx
        bool_results.append(file.endswith(".xlsx"))
        # logging.debug("Search for .xlsx resulted in %s", str(bool_results[1]))

        if all (results for results in bool_results):
            matches.append(file)
            logging.debug("The file %s matched the search parameters", file)

    return matches


def directory_search(course, assessment, main_dir, subdirs):
    """Search a list of directories for a course file

    This method uses find_grades_file multiple times to construct a dictionary
    of lists to return.

    Example Return::

        {
            "ENCM": ["ENGI 1040 Circuits Grade - ENCM.xlsx"],
            "Core": [
                "ENGI 1040 Circuits Grade - Core.xlsx",
                "ENGI 1040 Circuits Grade - Core - Custom column names.xlsx"
            ],
            "Co-op": [],
            "ECE": []
        }

    Args:
        course: The course number to search for (i.e. 'ENGI 3891')
        assessment: The assessment type to search for (i.e. 'Final Exam')
        main_dir: The path to the main search directory
        subdirs: The subdirectories to search

    Returns:
        results: A defaultdict of lists that contain all matches from a directory
    """
    results = defaultdict()

    for folder in subdirs:
        logging.debug("Searching folder %s", folder)
        # Run the find_grades_files function on the folder in the subdirectory
        ls = find_grades_files(course, assessment, os.listdir(main_dir + '/' + folder))
        results[folder] = []
        if ls:
            results[folder] += ls
    
    return results
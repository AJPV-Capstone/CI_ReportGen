"""Grades organization functions"""
import pandas as pd
import numpy as np
import os
from collections import defaultdict

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

    Returns:
        pd.DataFrame: a DataFrame containing the grades

    Exceptions:
        FileNotFoundError: Raises an error when the grades file cannot be opened
    """
    if not course_col_name:
        course_col_name = 'Course #'
    if not assessment_col_name:
        assessment_col_name = 'Method of Assessment'
    if not grades_top_folder:
        grades_top_folder = os.path.dirname(__file__) + '/Grades/'

    filename='{}/{}/{} {}.xlsx'.format(grades_top_folder, program, row[course_col_name], row[assessment_col_name])
    return pd.read_excel(filename)

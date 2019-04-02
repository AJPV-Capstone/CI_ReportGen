"""Grades organization functions"""
import pandas as pd
import os

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



'''
def separate_promo_sheet(year, grades_dir = None, file=None):
    """Separator for Engineering One promotion sheets

    Parses Engineering One promotion sheet and separates the data into different
    files. Expects to find promo sheets in current_directory/Grades/Core

    Args:
    	year: The year to process (defaults to the processor year; entering this
            value will redefine the processor year)
        grades_dir: The top folder of the grades. Used when finding file by
            year.
        file: The file to open. Overrides opening by year

    """
    # Open file if provided, otherwise run a search using the year
    if file:
        print("Opening promo file", file)
        promosheet = pd.read_excel(file)
    else:
        print("Finding promo file using year", year)
        promosheet_name = ""
        # Get a list of files in the Core folder
        files = os.listdir(self.gradesDir + "Core/")

        # Go through each file; look for the year and "EngOne"
        for file in files:
            if file.find(str(self.year)) != -1 and file.find("EngOne") != -1:
                promoFile = self.gradesDir + "Core/" + file
                break

            # After getting the file name, open it
            print("Opening file", promoFile)
            promosheet = pd.read_excel(promoFile)

        # If no courses were specified, use self.defaultCourses
        if courses == None:
            courses = self.defaultCourses
        # Clean up the list of courses for the program to iterate over them
        for courseName in courses:
            # If the course is English or Chemistry related, set it to the
            # promotion sheet format
            if courseName.find("ENGL") != -1:
                courseName = "English"
            elif courseName.find("CHEM") != -1:
                courseName = "Chemistry"
            else:
                # Remove spaces
                courseName = courseName.replace(' ','')
                # Set to all lowercase
                courseName = courseName.lower()
                # Capitalize first letter
                courseName = courseName.capitalize()

        # Iterate over the spreadsheet by course, adding grades to their
        # respective dictionaries
        for course in courses:
            print("Parsing course", course)
            for i, row in promosheet.iterrows():
                # temp variable to store discipline
                temp = ""
                # else-if chain to determine discipline
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
                    print("No discipline found for row " + str(i+2) + ", adding to ENUD")
                    temp = 'ENUD'

                # If the stored grade in the row is not an integer, add -1 to represent
                # no data available. Otherwise, save the row value
                self.data[course][temp].append(__parseGrade(row[course]))

        # Print finished message
        print ("Parsing finished")
'''

import pandas as pd
from collections import defaultdict
import os
import globals
import re
import logging

class DataStore(object):
    """Data Storage object

    An object that stores all of the indicator data in one place. This object was
    built to be replaced by a database interface (hence the name), and many of the
    methods reflect that. For example, the object has a query method.

    Attributes:
        indicators(dict(pd.DataFrame)): A dictionary of Pandas DataFrames that store
            the indicator information for each loaded program. The dictionary gets
            keyed by program
        indicators_loc(string): The path to the location of the indicator sheets
        grades_loc(string): The path to the top folder for the grade storage
        unique_courses(pd.DataFrame): A Pandas DataFrame that contains information
            on courses that do not follow the standard term offered rule or that are
            not stored in the usual format. Usually, the first integer in a course
            tag (e.g. ENGI 3424) indicates the term that course is offered. However,
            some courses like CHEM 1051 are taken in term 3. Any courses that do not
            have grades stored by academic year and term offered should also be in
            this table (e.g. MATH 2000 was pulled from Banner, and the grades are
            stored by cohort). The data gets loaded from an Excel file that the object
            looks for one directory above this one called "Unique Courses.xlsx"
        
    See Also:
        * :class:`.ReportConfig`
    """


    def __init__(self, programs = None, indicators_loc = None, grades_loc = None):
        """Initialization, load indicators

        Initializes the indicator DataFrame with data from the programs list

        Args:
            programs(list(string)): A list of strings containing the programs to
                load indicators for. Defaults to loading indicators for every program
            indicators_loc(string): The file location for the Indicator lists. Defaults to
                finding them in the project directory using OS.path
            grades_loc(string): The location of the grades sheets. Defaults to finding
                them in the project directory using OS.path
        """
        logging.info("Start of DataStore initialization")
        logging.info("Setting up location of Indicator lookup tables")
        if not indicators_loc:
            pth = os.path.dirname(__file__) + '/../Indicators'
            logging.debug("No indicator directory passed to the constructor - using %s", pth)
            self.indicators_loc = pth
        else:
            self.indicators_loc = indicators_loc

        logging.info("Loading indicator lookup tables from programs list")
        self.indicators = defaultdict()

        # Get a list of programs to open indicator files for
        if not programs:
            logging.debug("No program list passed to the constructor - using all programs")
            programs = globals.all_programs.copy()

        # Formatted string to open indicator files with
        filestring = "{pth}/{prgm} Indicators.xlsx"
        #------------------------------------------------------------------------------------
        # Iterate across the programs list and load the indicator files
        #------------------------------------------------------------------------------------
        for p in programs:
            logging.debug("Attempting to load indicators for %s using file %s",
                p, filestring.format(pth = self.indicators_loc, prgm = p)
            )
            self.indicators[p] = pd.read_excel(filestring.format(pth = self.indicators_loc, prgm = p))

        # Find out where to find the grades
        logging.info("Setting up location to find grades")
        if not grades_loc:
            pth = os.path.dirname(__file__) + '/../Grades'
            logging.debug("No grades location passed to the constructor, using %s", pth)
            self.grades_loc = pth
        else:
            self.grades_loc = grades_loc

        # Open the unique course file
        logging.info("Opening the Unique Courses file")
        self.unique_courses = pd.read_excel(os.path.dirname(__file__) + '/../Unique Courses.xlsx')

        logging.info("DataStore object initialization complete!")


    def query_indicators(self, program, dict_of_queries=None):
        """Query indicators sheet

        Queries a specific program's indicator list and returns a DataFrame
        containing all of the search results. The query behaves iteratively
        (i.e. it will query one option, then the next option, then the next,
        etc.).

        Args:
            program(string): The program to search for the indicator
            dict_of_queries(dict(list)): A dictionary of lists of things to
            query. The program will try to match up each dictionary key with
            the first column it finds that contains part of the key in the
            indicators DataFrame. If None, the method will not query and will
            just return the corresponding program's indicator DataFrame

        Returns:
            DataFrame: The DataFrame query
        """
        logging.info("Start of query_indicators method")
        # Try to set the last query to the program's indicators
        try:
            last_query = self.indicators[program]
        # If it doesn't work, try opening the program's indicators first
        except KeyError:
            logging.warning("Indicators for %s apparently not loaded. Loading now...", program)
            self.indicators[program] = pd.read_excel(self.indicators_loc + "/{} Indicators.xlsx".format(program))
            last_query = self.indicators[program]

        logging.debug("Querying %s", str(dict_of_queries))

        # Query iteratively using the dict keys
        if dict_of_queries:
            for key in dict_of_queries.keys():
                # Find the spreadsheet column that closely matches the dictionary key
                col = next((s for s in last_query.columns if key.lower() in s.lower()), None)
                logging.debug("Query for %s mapped to %s in indicator table", key, col)
                #---------------------------------------------------------------------------------
                # Query to take a value only if the query list entry contains part of the value.
                # The main thing here is that to get the value out, only part of the value in the
                # query list has to appear. It's done this way so that if you wanted to get all
                # 'KB' indicators, for example, you could do so by adding 'KB' to the list of
                # indicators to query
                #---------------------------------------------------------------------------------
                # Use a regular expression to get the parse to work
                pat = re.compile('|'.join(dict_of_queries[key]))
                query = last_query[col].str.contains(pat)
                last_query = last_query[query]    # Query the DataFrame
                logging.debug("Query for %s resulted in %d results", key, len(last_query.index))

        return last_query

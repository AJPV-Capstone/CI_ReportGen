import pandas as pd
from collections import defaultdict
import os
import globals
import re
import logging

class DataStore(object):
    """Data Storage object

    An object that stores all of the grades and indicator data in one place.
    Contains methods used to query information from the stored data, including
    indicator info, grades, and so on.

    Attributes:
        programs: A list of programs that the DataStore object
        indicators: A dictionary of Pandas DataFrames that store the master indicator
            lists for each program. These are typically loaded as needed to avoid
            unnecessary memory usage
        last_query: Stores the result from the last dictionary query to the indicators
            DataFrame
        indicators_loc: The location of the indicator sheets
        grades_loc: The top folder for the grade storage
        backup_file_lists: A dict of lists that stores the file names in the
            "Core" and "Co-op" grades subdirectories These lists are typically
            used as backup when the program cannot properly identify the right
            file in the normal directory.
    """


    def __init__(self, programs = None, indicators_loc = None, grades_loc = None):
        """Initialization, load indicators

        Initializes the indicator DataFrame with data from the programs list

        Args:
            programs: A list of strings containing the programs to load indicators
                for. Defaults to loading indicators for every program
            indicators_loc: The file location for the Indicator lists. Defaults to
                finding them in the project directory using OS.path
            grades_loc: The location of the grades sheets. Defaults to finding
                them in the project directory using OS.path

        """
        logging.info("Start of DataStore initialization")
        logging.info("Setting up location of Indicator lookup tables")
        if not indicators_loc:
            pth = os.path.dirname(__file__) + '/Indicators/'
            logging.debug("No indicator directory passed to the constructor - using %s", pth)
            self.indicators_loc = pth
        else:
            self.indicators_loc = indicators_loc

        logging.info("Setting up internal program list")
        if not programs:
            logging.debug("No program list passed to the constructor - using all programs")
            self.programs = globals.all_programs.copy()
        else:
            self.programs = programs

        logging.info("Loading indicator lookup tables now")
        self.indicators = defaultdict()
        filestring = "{} Indicators.xlsx" # Formatted string to open indicator files with
        for p in self.programs:
            # Try-except will prevent complete program crash when it doesn't find an
            # Indicator
            try:
                logging.debug("Attempting to load indicators for %s using file %s",
                        p, self.indicators_loc + filestring.format(p))
                self.indicators[p] = pd.read_excel(self.indicators_loc + filestring.format(p))
            except FileNotFoundError:
                logging.warning("The file %s was not found, therefore no indicators were loaded for it.",
                        self.indicators_loc + filestring.format(p))

        logging.info("Setting up location to find grades")
        if not grades_loc:
            pth = os.path.dirname(__file__) + '/Grades/'
            logging.debug("No grades location passed to the constructor, using %s", pth)
            self.indicators_loc = pth
        else:
            self.grades_loc = grades_loc

        logging.info("Storing file lists of the Core, Co-op and ECE directories")
        self.backup_file_lists = {
            'Core': os.listdir(self.grades_loc + 'Core/'),
            'Co-op': os.listdir(self.grades_loc + 'Co-op/'),
            'ECE': os.listdir(self.grades_loc + 'ECE/')
        }

        logging.info("DataStore object initialization complete!")


    def query_indicators(self, program, dict_of_queries):
        """Get indicator information for the report

        Queries a specific program's indicator list and returns a DataFrame
        containing all of the search results. The final query also gets internally
        stored in self.last_query.

        Args:
            program: The program to search for the indicator
            dict_of_queries: A dictionary of things to query. The dictionary keys
                should closely resemble the column names in the indicator sheets.
                You should be able to pass lists or single values to query.
                Defaults to not querying

        Returns:
            DataFrame: The DataFrame query
        """
        logging.info("Start of query_indicators method")
        try:
            self.last_query = self.indicators[program]
        except KeyError:
            logging.warning("Indicators for", program, "apparently not loaded. Loading now")
            self.indicators[p] = pd.read_excel(self.indicators_loc + filestring.format(p))
            self.last_query = self.indicators[program]

        # Query iteratively using the dict keys
        if dict_of_queries:
            for key in dict_of_queries.keys():
                # Find the spreadsheet column that closely matches the dictionary key
                col = next((s for s in self.last_query.columns if key.lower() in s.lower()), None)
                #---------------------------------------------------------------------------------
                # Query to take a value only if the query list entry contains part of the value.
                # The main thing here is that to get the value out, only part of the value in the
                # query list has to appear. It's done this way so that if you wanted to get all
                # 'KB' indicators, for example, you could do so by adding 'KB' to the list of
                # indicators to query
                #---------------------------------------------------------------------------------
                # Use a regular expression to get the parse to work
                pat = re.compile('|'.join(dict_of_queries[key]))
                query = self.last_query[col].str.contains(pat)
                self.last_query = self.last_query[query]    # Query the DataFrame

        return self.last_query

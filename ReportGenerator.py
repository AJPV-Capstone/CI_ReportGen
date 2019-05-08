from Report import Report
from ReportConfig import ReportConfig
from DataStore import DataStore
import grades_org
import globals
import textformatting as tf
import os
import numpy as np
import logging
import re
import pandas as pd
from collections import defaultdict


class ReportGenerator(object):
    """Assists with generating histogram reports

    Bundles all of the Report object generation things in one place and adds
    convenience methods for generation

    Attributes:
        config(ReportConfig): A ReportConfig object that the generator passes to each
            generated Report
        programs(list(string)): A list of programs (e.g. ENCM) to process.
        whitelist(dictionary): A dictionary including lists of the only things that should
            be processed. Options can include, but are not limited to, lists of:

                * Courses
                * Indicators
                * Assessments
                
            As long as the whitelist key matches closely to the column name in
            the indicator lookup table, it should be fine
        ds(DataStore): A DataStore object

        TODO:
            * Implement a blacklisting feature
    """


    def __init__(self, config, programs=None, cohorts=None, whitelist=None, ds=None,
            indicators_loc=None, grades_loc=None, histograms_loc=None,):
        """Object Initialization

        Args:
            config(ReportConfig): A ReportConfig object
            programs(string or list(string)): A list of programs to generate indicators for.
                Defaults to using all programs. If only one string is passed in, it will
                get put into a size-one list.
            cohorts(int or list(int)): A list of cohorts to pull data from. Defaults to
                using all cohorts. If only one cohort is passed in, it will get put into
                a size-one list.
            whitelist(dictionary): A dictionary of lists, keyed by the only stuff
                to parse (e.g. 'course', 'indicator', etc.) and filled with the
                specific values to uniquely parse. Defaults to no whitelist. The lists
                in the dictionaries can be partial (i.e. if you pass 'KB' as part of the
                'indicator' whitelist, it will pull all 'KB' indicators). If the
                lists contain only one string, that string gets put into a
                size-one list.
            ds(DataStore): A DataStore object. Defaults to generating one based on the
                whitelist entries for 'programs'
            indicators_loc(string): The location of the indicator sheets. Defaults to
                searching an "Indicators" folder in the directory above the project
                (see ReportConfig for more info)
            grades_loc(string): The location of the grades sheets. Defaults to searching
                a "Grades" folder in the directory above the project (see
                ReportConfig for more info)
            histograms_loc(string): The location to store histograms. Defaults to using
                a "Histograms" folder in the directory above the project (see
                ReportConfig for more info)
        """
        logging.info("Start of AutoGenerator initialization")
        self.config = config

        # logging.info("Initializing whitelist")
        self.whitelist = whitelist
        # Ensure that all whitelist entries are lists (if it exists, that is)
        if self.whitelist:
            logging.debug("Checking whitelist for list validity")
            for entry in self.whitelist.keys():
                self.whitelist[entry] = _check_list(self.whitelist[entry])

                # if type(self.whitelist[entry]) is not type(list()):
                #     logging.debug("Whitelist entry %s is not a list. Converting to a one-size list", entry)
                #     # Change to one-size list
                #     self.whitelist[entry] = [self.whitelist[entry]]

        # logging.info("Initializing cohorts list")
        self.cohorts = cohorts
        # Ensure that all cohorts entries are lists (if it exists, that is)
        if self.cohorts:
            logging.debug("Checking cohorts variable for list validity")
            self.cohorts = _check_list(self.cohorts)

        # logging.info("Initializing program list")
        self.programs = programs
        # Ensure list validity of programs
        if self.programs:
            logging.debug("Checking programs for list validity")
            self.programs = _check_list(self.programs)

        # Use all programs if none were provided
        if not self.programs:
            logging.debug("Programs not passed as paramater. Using list of all programs")
            self.programs = globals.all_programs

        # # Same check as whitelist - ensure that self.programs is a list
        # if type(self.programs) is not type(list()):
        #     logging.debug("Programs was not passed in list format. Converting to a one-size list")
        #     self.programs = [self.programs]

        # If any of the file location parameters were passed in, overwrite what ReportConfig has
        if indicators_loc:
            self.config.indicators_loc = indicators_loc
        if grades_loc:
            self.config.grades_loc = grades_loc
        if histograms_loc:
            self.config.histograms_loc = histograms_loc

        logging.debug("Indicators location is %s", self.config.indicators_loc)
        logging.debug("Grades location is %s", self.config.grades_loc)
        logging.debug("Histograms location is %s", self.config.histograms_loc)

        # Check to see if a DataStore was passed to init, create one if not
        if not ds:
            logging.debug("No DataStore object was passed to init; creating one now")
            self.ds=DataStore(programs=self.programs, indicators_loc=self.config.indicators_loc,
                    grades_loc=self.config.grades_loc)

        # Make sure that the histograms folder exists
        logging.info("Setting up output directories (Missing Data & Histograms)")
        os.makedirs(os.path.dirname(__file__) + '/../Missing Data', exist_ok=True)
        os.makedirs(self.config.histograms_loc, exist_ok=True)

        logging.info("ReportGenerator initialization done!")


    def _parse_row(self, row, program):
        """Turn a row of a Pandas DataFrame into a dictionary and bin list

        The data stored in the master indicator spreadsheets needs to be cleaned up
        properly for a Report object to use it. This function does that based on things
        in the ReportConfig. Program gets passed to the function because that is currently
        not stored in the indicators spreadsheet and needs to end up on the Report object
        somehow. This seemed like the most reasonable place to do it.

        ReportConfig.header_attribs determines what data gets pulled from the
        spreadsheet. For a single entry in header_attribs, multiple values
        could get pulled and concatenated from the spreadsheet row. For example,
        writing just 'Course' in the header_attribs would join the columns
        'Course #' and 'Course Description' using a ' - ' character

        Args:
            row(pd.Series): The row of a Pandas DataFrame (so a Pandas Series) to pull data from
            program(string): The program that the indicator file row belongs to

        Returns:
            dict: A dictionary containing the indicator information, keyed using instructions
            list(float): The bin ranges that have been converted from a comma-separated string
                to a list of floats. 0 gets appended to the front for NumPy histogram
            None, None: Returns 2 None values if non-number bins are found in the row
        """
        # logging.info("Parsing a row from a Pandas DataFrame")
        # Handle the bins first since those are easy
        try:
            bins = [float(x) for x in row['Bins'].split(',')]
        except Exception:
            logging.warning("ERROR: Non-number bins encountered in a lookup table")
            return None, None
        logging.debug("Bins parsed as:\t%s", ', '.join(str(x) for x in bins))

        # Convert the comma-separated string into dictionary keys
        # logging.info("Creating a dictionary of indicator information")
        indicator_dict = {i:"" for i in [x.strip() for x in self.config.header_attribs.split(',')]}

        # logging.info("Filling the dictionary with information from the row")
        for key in indicator_dict.keys():
            # Look for all occurrences where the key is found in the row's columns
            # and store that information in a list
            occurrences = [str(row[i]) for i in row.index if key in i]
            # Glue all collected data together with ' - ' characters
            # logging.debug("Indicator entry %s being filled with info from lookup table columns %s",
            #     key,
            #     ', '.join(occurrences)
            # )
            indicator_dict[key] = ' - '.join(occurrences)
            # logging.debug("Entry [%s]: %s", key, indicator_dict[key])
        
        # If Program is in indicator_dict, add the program parameter to indicator_dict
        if 'Program' in indicator_dict.keys():
            indicator_dict['Program'] = program

        # logging.info("Returning indicator dictionary and bins from this row")
        return indicator_dict, bins


    def start_autogenerate(self):
        """Begin autogeneration of reports

        The general procedure goes as follows:
        * Iterate across the stored indicator lookup tables:

          * Query the indicator table using the whitelist
          * Iterate through the query:

            * Get indicator data from the row
            * Search for grades for the assessment tool
            * Iterate through each file found and save a histogram

        TODO:
            * Decouple the method
            * Change the histogram file naming conventions to be shorter
            * Allow multiple assessment files to exist and get generated histograms
              (e.g. allow 'ENGI 1040 Circuits Grade' and 'ENGI 1040 Circuits Grade
              by Term' to both exist)
            * Allow customization of the file save name through ReportConfig
        """
        #------------------------------------------------------------------------------
        # Initial Autogeneration Setup
        #------------------------------------------------------------------------------

        logging.info("Beginning report autogeneration")
 
        logging.debug("Autogenerator set up to use programs %s", ', '.join(self.programs))

        # Iterate across the list of programs
        for program in self.programs:
            logging.info("Generating reports for program %s", program)

            # logging.info("Getting a query list from the program's indicator lookup table")
            # Query the indicators DataFrame
            query = self.ds.query_indicators(program=program, dict_of_queries=self.whitelist)

            #-----------------------------------------------------------------------
            # Get a list of files in the program's grades directory. The program
            # opens grades for the reports using file searching so that it can be
            # less restrictive on the naming conventions and use un-separated data
            # from other folders.
            #-----------------------------------------------------------------------
            # logging.info("Getting list of grade files in directory %s", self.config.grades_loc + '/' + program)
            
            # Search list set up as dictionary
            # logging.info("Setting up a search list hierarchy for finding and using grades")
            search_list = {program: os.listdir(self.config.grades_loc + '/' + program)}
            # Add the backup file lists (also in dict form) from DataStore
            search_list.update(self.ds.backup_file_lists)

            logging.debug("Searching for grades file in folders %s", ', '.join(search_list.keys()))

            # Set up a file to store missing data in
            # logging.info("Starting a file to save missing data")
            missing_data = open("../Missing Data/{} missing data.txt".format(program), "w+")

            # Iterate across each indicator (each row of the query)
            # logging.info("Beginning row iteration...")
            for rownumber, row in query.iterrows():
                
                # Skip this row if the "Assessed" column is set to any form of "No" (also check if it's there)
                if 'Assessed' in row and row['Assessed'].lower() == 'no':
                    # print("Found a non-assessed indicator")
                    continue

                # Skip this row if no bins are defined
                if row['Bins'] in [np.nan, None]:
                    logging.warning("No bins (and likely no data) found for {} {} {} {}, skipping row".format(
                        row['Indicator #'], row['Level'], row['Course #'], row['Method of Assessment']
                    ))
                    logging.warning("Missing binning stored in separate file")
                    # Log the missing data entry
                    missing_data.write("Missing bin ranges for {a} {b} ({c}-{d})\n".format(a=row["Course #"],
                        b=row["Method of Assessment"], c=row['Indicator #'], d=row['Level']
                    ))
                    continue
                else:
                    logging.debug("Processing data for {} {} {} {}".format(row['Indicator #'], row['Level'],
                        row['Course #'], row['Method of Assessment']
                    ))

                #------------------------------------------------------------------------------
                # Obtain the necessary indicator data and bins from the row. header_attribs in
                # ReportConfig determine what gets pulled and what doesn't. These are also 
                # JSON-loadable. Program gets added to indicator data later if required.
                #------------------------------------------------------------------------------
                indicator_data, bins = self._parse_row(row, program)
                # If no bins were parsed, a histogram cannot be generated. Skip this indicator/row
                if not bins:
                    logging.warning("ERROR: No useable bins for {} {} {} {}, skipping row".format(
                        row['Indicator #'], row['Level'], row['Course #'], row['Method of Assessment']
                    ))
                    # Log the missing bins
                    missing_data.write("No useable bins for {a} {b} ({c}-{d})\n".format(
                        a=row["Course #"], b=row["Method of Assessment"], c=row['Indicator #'], d=row['Level']
                    ))
                    continue

                logging.debug("Indicator data obtained from the row: %s", str(indicator_data))

                #-----------------------------------------------------------------------------
                # Use the search list to find grade files. Store all occurrences of the
                # assessment data so that a histogram can be generated for each data set.
                #
                # Generates a defaultdict like the following example:
                # {
                #     "ENCM": [],
                #     "Core": ["ENGI 1040 Circuits Grade - Core - Custom column names.xlsx"],
                #     "ECE": ["ENGI 1040 Circuits Grade - ECE - Custom column names.xlsx"]
                # }
                # These are stored in lists because the original intention was to allow
                # multiple assessment files for the same indicator. However, this has
                # (probably) not been implemented yet.
                #-----------------------------------------------------------------------------
                logging.debug("Beginning search for grade files. Priority: %s", ', '.join(search_list.keys()))

                found_grade_files = grades_org.directory_search(
                    course = row['Course #'],
                    assessment = row['Method of Assessment'],
                    main_dir = self.config.grades_loc,
                    # Use the config parameter to get the other backup subdirectories
                    subdirs = [program] + [x.strip() for x in self.config.grade_backup_dirs.split(',')]
                )

                # If the lists are empty, add data entry to missing data file
                if not any(found_grade_files[k] for k in found_grade_files.keys()):
                    missing_thing = "{a} {b} ({c}-{d})".format(
                        a=row["Course #"],
                        b=row["Method of Assessment"],
                        c=row['Indicator #'],
                        d=row['Level']
                    )
                    logging.warning("No data found for %s", missing_thing)
                    missing_data.write("Missing data for {}\n".format(missing_thing))
                    #-----------------------------------------------------------------------------
                    # Set up the found_grade_files dictionary in a way that the program will
                    # recognize as missing data and generate a blank histogram for
                    #-----------------------------------------------------------------------------
                    found_grade_files = {program: [None]}
                else:
                    logging.debug("Found files in %s", ', '.join(found_grade_files.keys()))

                # Check the unique course table to see if the course has a unique term offering
                term_offered = None
                for unique_course_rownum, unique_course in self.ds.unique_courses.iterrows():
                    if row['Course #'] == unique_course['Course #']:
                        term_offered = unique_course['Term Offered']
                        break
                
                #-----------------------------------------------------------------------------
                # Iterate across the list of grade files found and separately generate a
                # histogram for each file. Referring to the grade file keys as the location
                # at which the grades file was found. Generates a blank histogram in cases
                # where no data was found.
                #-----------------------------------------------------------------------------
                for location in found_grade_files.keys():
                    for file in range(0, len(found_grade_files[location])):
                        # Provide DataFrame to generate empty histograms if no data is found
                        if isinstance(found_grade_files[location][file], type(None)):
                            grades = pd.DataFrame({'NO DATA FOUND': [-1]})
                        else:   # Open the grades normally
                            grades = pd.read_excel("{}/{}/{}".format(
                                self.config.grades_loc,
                                location,
                                found_grade_files[location][file]
                                )
                            )
                            # Ready the DataFrame for histogramming
                            grades = self._ready_DataFrame(
                                grades,
                                course=row['Course #'],
                                term_offered=term_offered
                            )

                        #-----------------------------------------------------------------------------
                        # If the program that is being iterated across does not match the folder that
                        # the data was found, that should be indicated. The program entry in the
                        # header will always be based on which indicator lookup table the information
                        # came from. A note gets added to the header information in the case that data
                        # does not come from the same thing. Additionally, the program that the
                        # indicator belongs to will always get a copy of the file saved to their
                        # histgograms directory.
                        #-----------------------------------------------------------------------------
                        save_copies_to = [program]
                        if location != program:
                            indicator_data['Note'] = "Using data from {}".format(location)
                            logging.debug("Additional copy of this histogram being saved to %s", location)
                            save_copies_to.append(location)

                        # Generate the Report object
                        logging.debug("Generating histogram from %s/%s/%s",
                            self.config.grades_loc,
                            location,
                            found_grade_files[location][file]
                        )
                        report = Report.generate_report(indicator_data, bins, self.config, grades)

                        #------------------------------------------------------------------------
                        # Save the report with a file name reflective of the program, indicator
                        # and assessment type to the location that the data came from as well as
                        # the program subfolder that the indicator data belongs to. In the case
                        # Where multiple grade files were found, add a mumber to the file name.
                        #------------------------------------------------------------------------
                        # File name formatted string setup
                        if len(save_copies_to) > 1:
                            # histogram_name = "{pth}/{saveloc}/{prgm} {ind}-{lvl} {crs} {asmt}_{i} {cfg}.pdf"

                            # File name that reflects row number in indicator sheet and just the indicator
                            histogram_name = "{pth}/{saveloc}/{prgm} {row} {ind}-{lvl} datafrom_{dataloc} {cfg}"
                        else:
                            # histogram_name= "{pth}/{saveloc}/{prgm} {ind}-{lvl} {crs} {asmt} {cfg}.pdf"

                            # File name that reflects row number in indicator sheet and just the indicator
                            histogram_name = "{pth}/{saveloc}/{prgm} {row} {ind}-{lvl} {cfg}"

                        # Save iteration
                        for i in range (0, len(save_copies_to)):
                            # File name formatted string formatting
                            save_as = histogram_name.format(
                                pth = self.config.histograms_loc,
                                saveloc = save_copies_to[i],
                                prgm = program,
                                ind = row["Indicator #"],
                                lvl = row["Level"][0],
                                crs = row["Course #"],
                                asmt = row["Method of Assessment"],
                                i = i,
                                cfg = self.config.name,
                                # row is rownumber + 2 because Pandas indexes from 0 starting from row 2 in
                                # the original spreadsheet. zfill adds padding zeros
                                row = str(rownumber + 2).zfill(3),
                                dataloc = location
                            )
                            # Make sure the save directory exists, then save the file
                            os.makedirs("{pth}/{key}".format(
                                pth = self.config.histograms_loc,
                                key = save_copies_to[i]
                            ),
                            exist_ok=True
                            )
                            report.save(save_as)

        logging.info("Autogeneration done!")


    def _ready_DataFrame(self, grades, course, term_offered):
        """Pretty up a DataFrame for histogramming

        This method:
            * Turns DataFrame columns into cohort messages to act as legend entries
            * Filters cohorts if required
            * Indicates if a cohort has no data available
        
        The columns should look something like below normally:

        +--------+--------+--------+
        | 201603 | 201703 | 201803 |
        +========+========+========+

        The method will turn these into cohort messages and use cohort filterings. If
        a requested cohort does not appear in the grades files, a No Data column will
        get added for that cohort.

        Args:
            grades(DataFrame): The grades that were just loaded
            course(string): The course number
            term_offered(int): The term that the course is offered
        
        Returns:
            DataFrame: The prettied-up DataFrame
        """
        # Try changing the the DataFrame columns to cohort messages.
        try:
            grades.columns = grades_org.cols_to_cohorts(
                grades=grades,
                course_name = course,
                course_term_offered = term_offered
            )
        # If the columns names were not integer-convertible, append size and move on
        except Exception:
            logging.debug("Grade columns for this assessment of %s were not integers. " \
                + "Appending column sizes to original column names",
                course
            )
            # Uses a list comprehension to append the column's true size to the message
            grades.columns = ["{crs}({sz})".format(
                crs = entry,
                sz = grades_org.true_size(grades[entry])
                ) for entry in grades.columns
            ]
    
        # If a cohort filter is in place, take the columns that have the correct cohort(s)
        if self.cohorts is not None:
            logging.debug("Detected a cohort filter for cohorts %s", ', '.join([str(c) for c in self.cohorts]))
            # Start a list to append relevant DataFrame columns to
            new_grades_cols = []
            # Iterate across each cohort requested
            for c in self.cohorts:
                # Iterate across the grades DataFrame columns
                occurrences = 0
                for col in grades.columns:
                    if str(c) in col:
                        new_grades_cols.append(grades[col])
                        occurrences += 1
                        logging.debug("Matched cohort %s with column %s", str(c), col)
                # If no matching columns are found, append an NDA column
                if occurrences is 0:
                    logging.warning("No grades columns were matched to cohort %s", str(c))
                    new_grades_cols.append(pd.Series([-1], name="Co{}: NDA".format(str(c))))
            # Create a new DataFrame by concetenating all columns
            grades = pd.concat(new_grades_cols, axis=1, keys = [s.name for s in new_grades_cols])
        
        return grades



    @staticmethod
    def autogenerate(config, programs=None, cohorts=None, whitelist=None, ds=None,
            indicators_loc=None, grades_loc=None, histograms_loc=None,):
        """Shortcut to start histogram generation

        Initializes a ReportGenerator object and immediately starts report generation.

        TODO:
            * Create the method
        """
        pass


def _check_list(var):
    """Check a variable to see if it's a list and convert to a list if it's not

    Checks a parameter to see if it's a list. If it's not a list, it gets converted
    to a one-size list

    Args:
        var: The parameter to type check

    Returns:
        var if var was a list, [var] if var was not a list
    """
    if not isinstance(var, list):
        logging.debug("Variable %s was not a list. Converting to one-size list now...", str(var))
        var = [var]
    return var

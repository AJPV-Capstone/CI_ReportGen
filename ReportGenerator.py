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
    """Report Generator Class

    Bundles all of the Report object generation things in one place and adds
    convenience methods for generation

    Attributes:
        config: A ReportConfig object
        programs: A list of programs to process
        whitelist: A dictionary including lists of the only things that should
            be processed. Options can include, but are not limited to, lists of:
            - courses
            - indicators
            - assessments
            As long as the whitelist key matches closely to the column name in
            the indicator lookup table, it should be fine
        ds: A DataStore object

        Todo:
            - Implement a blacklisting feature
    """


    def __init__(self, config, year=None, semester=None, programs=None, whitelist=None, ds=None,
            indicators_loc=None, grades_loc=None, histograms_loc=None):
        """Object Initialization

        A whole bunch of the parameters for this init don't actually do anything
        right now. That should probably just get cleaned up.

        Args:
            config: A ReportConfig object
            indicators_loc: The location of the indicator sheets. Defaults to
                searching an "Indicators" folder in the directory above the
                project (see ReportConfig documentation for more info)
            grades_loc: The location of the grades sheets. Defaults to searching
                a "Grades" folder in the directory above the project (see
                ReportConfig documentation for more info)
            histograms_loc: The location to store histograms. Defaults to using
                a "Histograms" folder in the directory above the project (see
                ReportConfig documentation for more info)
            year: The academic year that data is being parsed for, or in some cases
                depending on config, the cap year on grade generation. Defaults
                to None
            semester: An integer from 1 to 3 indicating the semester. Defaults
                to None
            programs: A list of programs to generate indicators for. Defaults to
                using all programs. The passed list should be a list of strings,
                but if only one string is passed in, it will get put into a
                size-one list.
            whitelist: A dictionary of lists, keyed by the only stuff to parse (i.e.
                'course', 'indicator', etc.) and filled with the specific values
                to uniquely parse. Defaults to no whitelist. The lists in the
                dictionaries can be partial (i.e. if you pass 'KB' as part of the
                'indicator' whitelist, it will pull all 'KB' indicators). If the
                lists contain only one string, that string gets put into a
                size-one list.
            ds: A DataStore object. Defaults to generating one based on the
                whitelist entries for 'programs'
        """
        logging.info("Start of AutoGenerator initialization")
        self.config = config

        logging.info("Initializing whitelist")
        self.whitelist = whitelist
        # Ensure that all whitelist entries are lists (if it exists, that is)
        if whitelist:
            for entry in self.whitelist.keys():
                if type(self.whitelist[entry]) is not type(list()):
                    logging.debug("Whitelist entry %s is not a list. Converting to a one-size list", entry)
                    # Change to one-size list
                    self.whitelist[entry] = [self.whitelist[entry]]

        logging.info("Initializing program list")
        self.programs = programs

        # Use all programs if none were provided
        if not self.programs:
            logging.debug("Programs not passed as paramater. Using list of all programs")
            self.programs = globals.all_programs

        # Same check as whitelist - ensure that self.programs is a list
        if type(self.programs) is not type(list()):
            logging.debug("Programs was not passed in list format. Converting to a one-size list")
            self.programs = [self.programs]

        # If any of the file location parameters were passed in, overwrite what
        # the ReportConfig object has
        if indicators_loc:
            self.config.indicators_loc = indicators_loc
        if grades_loc:
            self.config.grades_loc = grades_loc
        if histograms_loc:
            self.config.histograms_loc = histograms_loc

        logging.debug("Indicators location is %s", self.config.indicators_loc)
        logging.debug("Grades location is %s", self.config.grades_loc)
        logging.debug("Histograms location is %s", self.config.histograms_loc)

        # Check to see if a DataStore was passed to the function
        if not ds:
            logging.debug("No DataStore object was passed to the function; creating one now")
            self.ds=DataStore(programs=self.programs, indicators_loc=self.config.indicators_loc,
                    grades_loc=self.config.grades_loc)

        # Make sure that the histograms folder exists as the program writes to it
        logging.info("Setting up output directories (Missing Data & Histograms)")
        os.makedirs(os.path.dirname(__file__) + '/../Missing Data', exist_ok=True)
        os.makedirs(self.config.histograms_loc, exist_ok=True)

        logging.info("ReportGenerator initialization done!")


    def _parse_row(self, row):
        """Turn a row of a Pandas DataFrame into a dictionary and bin list

        The data stored in the master indicator spreadsheets needs to be cleaned up
        properly for a Report to use it. This function does that based on things
        in the ReportConfig.

        - ReportConfig.header_attribs determines what data gets pulled from the
          spreadsheet. For a single entry in header_attribs, multiple values
          could get pulled and concatenated from the spreadsheet row. For example,
          writing just 'Course' in the header_attribs would join the columns
          'Course #' and 'Course Description' using a ' - ' character

        Args:
            row: The row of a Pandas DataFrame (so a Pandas Series) to clean up

        Returns:
            dict: A dictionary containing the indicator information, keyed using instructions
            list(float): The bin ranges that have been converted from a comma-separated string
                to a list of floats. 0 gets appended to the front for NumPy histogram

        Todo:
            - Document the exceptions
        """
        logging.info("Parsing a row from a Pandas DataFrame")
        # Handle the bins first since those are easy
        try:
            bins = [float(x) for x in row['Bins'].split(',')]
        except Exception:
            logging.warning("ERROR: Non-number bins encountered in a lookup table")
            return None, None
        logging.debug("Bins parsed as:\t%s", ', '.join(str(x) for x in bins))

        # Convert the comma-separated string into dictionary keys
        logging.info("Creating a dictionary of indicator information")
        indicator_dict = {i:"" for i in [x.strip() for x in self.config.header_attribs.split(',')]}

        logging.info("Filling the dictionary with information from the row")
        for key in indicator_dict.keys():
            # Look for all occurrences where the key is found in the row's columns
            # and store that information in a list
            occurrences = [str(row[i]) for i in row.index if key in i]
            # Glue all collected data together with ' - ' characters
            logging.debug("Indicator entry %s being filled with info from lookup table columns %s",
                key,
                ', '.join(occurrences)
            )
            indicator_dict[key] = ' - '.join(occurrences)
            logging.debug("Entry [%s]: %s", key, indicator_dict[key])

        logging.info("Returning indicator dictionary and bins from this row")
        return indicator_dict, bins


    def autogenerate(self):
        """Begin autogeneration of reports

        The general procedure goes as follows:
        
        Iterate across the stored indicator lookup tables:
            Query the indicator table using the whitelist
            Iterate through the query:



        Todo:
            - Implement other ways to set up the grades
            - Make get_cohort call less bad
        """
        #------------------------------------------------------------------------------
        # Initial Autogeneration Setup
        #------------------------------------------------------------------------------

        logging.info("Beginning report autogeneration")
        # If the autogeneration is not plotting grades by year, do different things
        # with the way that autogeneration iterates?
        logging.debug("Autogenerator set to plot grades by %s from ReportConfig", self.config.plot_grades_by)
        if self.config.plot_grades_by != 'year':
            raise NotImplementedError("Cannot plot grades by any type other than year")
        else:
            iterprograms = self.programs
        logging.debug("Autogenerator set up to use programs: %s", ', '.join(iterprograms))

        # Iterate across the list of programs
        for program in iterprograms:
            logging.info("Generating reports for program %s", program)

            logging.info("Getting a query list from the program's indicator lookup table")
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
            logging.info("Starting a file to save missing data")
            missing_data = open("../Missing Data/{} missing data.txt".format(program), "w+")

            # Iterate across each indicator (each row of the query)
            logging.info("Beginning row iteration...")
            for i, row in query.iterrows():
                
                # Skip this row if the "Assessed" column is set to any form of "No"
                if row['Assessed'].lower() == 'no':
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
                # Obtain the necessary indicator data and bins from the row. The header
                # attribs in ReportConfig determine what gets pulled and what doesn't.
                # These header attribs are also JSON-loadable.
                #------------------------------------------------------------------------------
                indicator_data, bins = self._parse_row(row)
                indicator_data['Program'] = program
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
                #     "ECE": ["ENGI 1040 Circuits Grade - Core - Custom column names.xlsx"]
                # }
                # These are stored in lists because the original intention was to allow
                # multiple assessment files for the same indicator. However, this has
                # (probably) not been implemented due to time constraints.
                #-----------------------------------------------------------------------------
                logging.debug("Beginning search for grade files. Priority: %s", ', '.join(search_list.keys()))

                found_grade_files = grades_org.directory_search(
                    course = row['Course #'],
                    assessment = row['Method of Assessment'],
                    main_dir = self.config.grades_loc,
                    # Use the config parameter to get the other backup subdirectories
                    subdirs = [program] + [x.strip() for x in self.config.grade_backup_dirs.split(',')]
                )

                # If the lists are empty, add data entry to missing data file and continue
                if not any(found_grade_files[k] for k in found_grade_files.keys()):
                    missing_thing = "{a} {b} ({c}-{d})".format(
                        a=row["Course #"],
                        b=row["Method of Assessment"],
                        c=row['Indicator #'],
                        d=row['Level']
                    )
                    logging.warning("No data found for %s. Skipping this indicator", missing_thing)
                    missing_data.write("Missing data for {}\n".format(missing_thing))
                    continue
                else:
                    logging.debug("Found files in %s", ', '.join(found_grade_files.keys()))

                # Check the unique course table to see if the course has a unique term offering
                term_offered = None
                for i, unique_course in self.ds.unique_courses.iterrows():
                    if row['Course #'] == unique_course['Course #']:
                        term_offered = unique_course['Term Offered']
                        break
                
                #-----------------------------------------------------------------------------
                # Iterate across the list of grade files found and separately generate a
                # histogram for each file. Referring to the grade file keys as the location
                # at which the grades file was found.
                #-----------------------------------------------------------------------------
                for location in found_grade_files.keys():
                    for file in range(0, len(found_grade_files[location])):

                        # Open the grades
                        grades = pd.read_excel("{}/{}/{}".format(
                            self.config.grades_loc,
                            location,
                            found_grade_files[location][file]
                            )
                        )

                        # Try changing the the DataFrame columns to cohort messages
                        try:
                            grades.columns = grades_org.cols_to_cohorts(
                                grades=grades,
                                course_name = row['Course #'],
                                course_term_offered = term_offered
                            )
                        # If the columns names were not integer-convertible, append size and move on
                        except Exception:
                            logging.debug("Grade columns for %s %s were not integers. " \
                                + "Appending column sizes to original column names",
                                row["Course #"],
                                row["Method of Assessment"]
                            )
                            # Use a list comprehension to append the column's true size to the message
                            grades.columns = ["{c}({s})".format(
                                c = entry,
                                s = grades_org.true_size(grades[entry])
                                ) for entry in grades.columns
                            ]

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
                        if len(save_copies_to) > 1:
                            histogram_name = "{pth}/{loc}/{p} {ind}-{lvl} {crs} {asmt}_{i} {cfg}.pdf"   
                        else:
                            histogram_name= "{pth}/{loc}/{p} {ind}-{lvl} {crs} {asmt} {cfg}.pdf"

                        for i in range (0, len(save_copies_to)):
                            save_as = histogram_name.format(
                                pth = self.config.histograms_loc,
                                loc = save_copies_to[i],
                                p = program,
                                ind = row["Indicator #"],
                                lvl = row["Level"][0],
                                crs = row["Course #"],
                                asmt = row["Method of Assessment"],
                                i = i,
                                cfg = self.config.name
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

from Report import Report
from ReportConfig import ReportConfig
from DataStore import DataStore
import grades_org
import globals
import textformatting as tf
import os
import numpy as np

class ReportGenerator(object):
    """Report Generator Class

    Bundles all of the Report object generation things in one place and adds
    convenience methods for generation

    Attributes:
        config: A ReportConfig object
        whitelist: A dictionary including lists of the only things that should
            be processed. Options can include, but are not limited to, lists of:
            - programs
            - courses
            - indicators
            - assessments
        ds: A DataStore object

    Notes:
        - Both a blacklist and a whitelist can be passed into the object.
        However, in cases where a value comes up in both the whitelist and the
        blacklist, the blacklist will have the final say.

        Todo:
            - Implement the blacklisting feature
    """


    def __init__(self, config, year=None, semester=None, whitelist=None, ds=None,
            indicators_loc=None, grades_loc=None, histogram_store=None):
        """Object Initialization

        Args:
            config: A ReportConfig object
            year: The academic year that data is being parsed for, or in some cases
                depending on config, the cap year on grade generation. Defaults
                to None
            semester: An integer from 1 to 3 indicating the semester. Defaults
                to None
            whitelist: A dictionary of lists, keyed by the only stuff to parse (i.e.
                'program', 'course', etc.) and filled with the specific values
                to uniquely parse. Defaults to no whitelist
            ds: A DataStore object. Defaults to generating one based on the
                whitelist and blacklist entries for 'programs'
            indicators_loc: The location of the indicator sheets
            grades_loc: The location of the grades sheets
            histogram_store: The location to store histograms. Defaults to making
                a histograms folder in the current directory

            Todo:
                - Implement blacklisting
                - Make error messages more descriptive
        """
        self.config = config
        #self.blacklist = blacklist
        self.whitelist = whitelist
        # Create a list of indicator sheet queries from whatever was passed in
        # with the whitelist
        self.indicator_queries = whitelist.copy()
        # Pop program whitelisting off
        self.indicator_queries.pop('programs', None)
        # Initialize a DataStore using the whitelists and blacklists if they exist
        if not ds:
            #if self.blacklist['programs']: # if a programs blacklist exists
            #    self.ds=DataStore(programs=[p for p in globals.all_programs if p not in self.blacklist['program']],
            #            indicators_loc=indicators_loc, grades_loc=grades_loc)
            if self.whitelist['programs']: #if a program whitelist exists
                self.ds=DataStore(programs=self.whitelist['programs'], indicators_loc=indicators_loc,
                        grades_loc=grades_loc)
            else:
                # Generate DataStore with all program indicators
                self.ds=DataStore(indicators_loc=indicators_loc, grades_loc=grades_loc)
        if not histogram_store:
            self.histogram_store = "Histograms/"
            os.makedirs(self.histogram_store, exist_ok=True)
        else:
            self.histogram_store = histogram_store


    def _parse_row(self, row):
        """Turn a row of a Pandas DataFrame into a dictionary and bin list

        The data stored in the master indicator spreadsheets needs to be cleaned up
        properly for a Report to use it. This function does that based on things
        in the ReportConfig

        Args:
            row: The row of a Pandas DataFrame (so a Pandas Series) to clean up

        Returns:
            dict: A dictionary containing the indicator information, keyed using instructions
            list(float): The bin ranges that have been converted from a comma-separated string
                to a list of floats. 0 gets appended to the front for NumPy histogram
        """
        # Handle the bins first since those are easy
        bins = [float(x) for x in row['Bins'].split(',')]

        # Convert the comma-separated string into dictionary keys
        indicator_dict = {i:"" for i in [x.strip() for x in self.config.header_attribs.split(',')]}

        for key in indicator_dict.keys():
            # Look for all occurrences where the key is found in the row's columns
            # and store that information in a list
            occurrences = [str(row[i]) for i in row.index if key in i]
            # Glue all collected data together with ' - ' characters
            indicator_dict[key] = ' - '.join(occurrences)

        return indicator_dict, bins


    def autogenerate(self):
        """Begin autogeneration of reports

        Todo:
            - Implement other ways to set up the grades
            - Make get_cohort call less bad

        Bugs:
            - Pretty sure that the graphs are not properly determining cohort.
                Review the get_cohort function from textformatting and formally
                test it.
        """
        # If the autogeneration is not plotting grades by year, do different things
        # with the way that autogeneration iterates
        if self.config.plot_grades_by != 'year':
            # Select a specific indicator sheet to query
            iterprograms = [self.config.use_indicators_from]
        else:
            iterprograms = self.ds.programs

        # Iterate across the list of programs
        for program in iterprograms:
            self.ds.query_indicators(program=program, dict_of_queries=self.indicator_queries)
            # Iterate across each indicator (each row)
            for row in self.ds.last_query.iterrows():
                # Skip this row if no bins are defined
                if row[1]['Bins'] in [np.nan, None, '!', '!!', '!!!']:
                    print("No bins found for {} {}, skipping".format(row[1]['Indicator #'], row[1]['Level']))
                    continue
                # Obtain the necessary indicator data and bins
                indicator_data, bins = self._parse_row(row[1])
                indicator_data['Program'] = program

                # Get the right data into a DataFrame
                if self.config.plot_grades_by != 'year':
                    raise NotImplementedError("Attempted to parse grades by a way that isn't year")
                else:
                    try:
                        grades = grades_org.open_grades(row[1], program)
                    except Exception as exc:
                        print(exc)
                        print("Skipping this course and continuing")
                        continue
                # Rename the DataFrame columns by cohort for now
                # Uses a long annoying list comprehension right now
                grades.columns = ["{}COHORT-{} STUDENTS".format(
                    tf.get_cohort(i, course=indicator_data['Course'].split(' - ')[0]),
                    grades[i].size) for i in grades.columns
                ]
                # Generate Report and add annotations depending on configuration
                report = Report(indicator_data, bins, self.config)
                report.add_header()
                report.plot(grades)
                if self.config.add_bin_ranges:
                    report.add_bin_ranges()
                if self.config.add_title:
                    report.add_title()
                report.save(self.histogram_store + "{}-{} Report - {}.pdf".format(
                    indicator_data['Indicator'].split('-')[0].strip(), indicator_data['Level'][0],
                    self.config.name))

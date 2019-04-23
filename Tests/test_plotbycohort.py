"""Plot by cohort test

Author: Ryan Letto (rmletto)
Last Modified: Apr. 18, 2019

Changes:
    Apr. 18, 2019 (rmletto): Realized that since these tests may deprecate automatically,
        I should document when they change. As of today, this one does not run and can
        be considered deprecated.

"""

# Temp import for testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from Report import Report
from ReportConfig import ReportConfig
from DataStore import DataStore
import pandas as pd
import unsorted
import datetime

print("Loading ENCV indicators into DataStore")
ds = DataStore(['ENCV'])

print("Querying KB.1-D")
ds.query_indicators(program = 'ENCV', indicator = 'KB.1', level='D')

config = ReportConfig()

'''
print("Removing the NDA threshold")
config.NDA_threshold = 0.0
'''
for row in ds.last_query.iterrows():
    print("Processing course",row[1]["Course #"])

    indicator_data, bins = unsorted.parse_row(row[1], config.header_attribs)
    indicator_data['Program'] = 'ENCV'

    print("Indicator data and bins set up, looking for grades")
    grades = unsorted.open_grades(row[1], 'ENCV')

    print("Reformatting column names of grades")
    grades.columns = ["{}COHORT-{} STUDENTS".format(unsorted.get_cohort(i, course=indicator_data['Course'].split(' - ')[0]), grades[i].size) for i in grades.columns]
    print(grades)

    print("Generating report and plotting data")
    report = Report(indicator_data, bins, config)
    report.plot(grades)

    print("Adding bin ranges")
    report.add_bin_ranges()

    print("Adding header annotation")
    report.add_header()

    print("Adding title")
    report.add_title()

    print("Saving Report")
    report.save("Test1 generation query 1 - {}.pdf".format(datetime.datetime.now()))

'''
print("Doing all of that report generation again, but disabling the NDA bin")
config.show_NDA = False
for row in ds.last_query.iterrows():
    print("Processing course",row[1]["Course #"])

    indicator_data, bins = unsorted.parse_row(row[1], config.header_attribs)
    indicator_data['Program'] = 'ENCV'

    print("Indicator data and bins set up, looking for grades")
    grades = unsorted.open_grades(row[1], 'ENCV')

    print("Reformatting column names of grades")
    grades.columns = ["{}COHORT-{} STUDENTS".format(unsorted.get_cohort(i, course=indicator_data['Course'].split(' - ')[0]), grades[i].size) for i in grades.columns]
    print(grades)

    print("Generating report and plotting data")
    report = Report(indicator_data, bins, config)
    report.plot(grades)

    print("Adding bin ranges")
    report.add_bin_ranges()
    print(report._annotations)

    print("Adding header annotation")
    report.add_header()
    print(report._annotations)

    print("Saving Report")
    report.save("Test1 generation wo NDA - {}.pdf".format(datetime.datetime.now()))
'''

print("Generating a new query: The KB indicator that maps to ENGI 4425 in ENCV")
ds.query_indicators(program='ENCV', indicator='KB', course='ENGI 4425')

for row in ds.last_query.iterrows():
    print("Processing course",row[1]["Course #"])

    indicator_data, bins = unsorted.parse_row(row[1], config.header_attribs)
    indicator_data['Program'] = 'ENCV'

    print("Indicator data and bins set up, looking for grades")
    grades = unsorted.open_grades(row[1], 'ENCV')

    print("Reformatting column names of grades")
    grades.columns = ["{}COHORT-{} STUDENTS".format(unsorted.get_cohort(i, course=indicator_data['Course'].split(' - ')[0]), grades[i].size) for i in grades.columns]
    print(grades)

    print("Generating report and plotting data")
    report = Report(indicator_data, bins, config)
    report.plot(grades)

    print("Adding bin ranges")
    report.add_bin_ranges()

    print("Adding header annotation")
    report.add_header()

    print("Adding title")
    report.add_title()

    print("Saving Report")
    report.save("Test1 generation query 2 - {}.pdf".format(datetime.datetime.now()))

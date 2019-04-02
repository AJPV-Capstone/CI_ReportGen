"""Test for the get_cohort function"""
# Temp import for testing
import sys
sys.path.insert(0, '/Users/ryanletto/Desktop/WT2/CI_ReportGen')

from textformatting import get_cohort

courses = [
    'ENGI1010',
    'MATH2050',
    'ENGI3424',
    'ENGI4425',
    'ENGI5000',
    'ENGI6000',
    'ENGI7000',
    'ENGI8000'
]

year = 2017
print("Using academic year", year)
for course in courses:
    print("Cohort for {}:\t {}".format(course, get_cohort(year, course=course)))


year = 201703
print("Using academic year", year)
for course in courses:
    print("Cohort for {}:\t {}".format(course, get_cohort(year, course=course)))

year = 201801
print("Using academic year", year)
for course in courses:
    print("Cohort for {}:\t {}".format(course, get_cohort(year, course=course)))

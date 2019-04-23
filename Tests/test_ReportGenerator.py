"""Plot by cohort test using the ReportGenerator object

Author: Ryan Letto (rmletto)
Last Modified: Apr. 18, 2019

Changes:
    Apr. 18, 2019 (rmletto): Realized that since these tests may deprecate automatically,
        I should document when they change. As of today, this one should run and work
        as intended (not tested). However, most of this code was implemeted as part of
        procedures.histogram_by_cohort() some time ago, so it's fairly useless now
"""

# Temp import for testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from ReportGenerator import ReportGenerator
from ReportConfig import ReportConfig

print("Setting up the indicator whitelist")
whitelist = {
    'programs': ['ENCV'],
    'indicator': ['KB']
}

print("Setting up ReportConfig")
config = ReportConfig()

print("Initializing ReportGenerator")
gen = ReportGenerator(config, whitelist=whitelist)

print("Running autogenerate")
gen.autogenerate()

"""Plot by cohort test using the ReportGenerator object

Todo:
    - Make all of the method calls more verbose for easier error tracking
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

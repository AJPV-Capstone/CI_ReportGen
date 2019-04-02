"""Plot by cohort test using the ReportGenerator object

Todo:
    - Make all of the method calls more verbose for easier error tracking
"""

# Temp import for testing
import sys
sys.path.insert(0, '/Users/ryanletto/Desktop/WT2/CI_ReportGen')

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

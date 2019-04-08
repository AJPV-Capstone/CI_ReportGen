"""Function test for textformatting.get_cohort_coop"""

# Temp import for testing
import sys
sys.path.insert(0, '/Users/ryanletto/Desktop/WT2/memorial-ece ReportGen/CI_ReportGen')

import textformatting as tf

WTs = [1,2,3,4]

years_and_semesters = [201701, 201702, 201703, 201801, 201802, 201803]

for yas in years_and_semesters:
    print("Testing {}".format(str(yas)))
    for wt in WTs:
        print("Work term {} maps to cohort {}", str(wt), tf.get_cohort_coop(yas, wt))

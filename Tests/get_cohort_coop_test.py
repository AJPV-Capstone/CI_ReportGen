"""Function test for textformatting.get_cohort_coop

Author: Ryan Letto (rmletto)
Last Modified: Apr. 18, 2019

Changes:
    Apr. 18, 2019 (rmletto): Realized that since these tests may deprecate automatically,
        I should document when they change. As of today, this one runs and works
        as intended.

"""

# Temp import for testing
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

import textformatting as tf

WTs = [1,2,3,4]

years_and_semesters = [201701, 201702, 201703, 201801, 201802, 201803]

for yas in years_and_semesters:
    print("Testing {}".format(str(yas)))
    for wt in WTs:
        print("Work term {} maps to cohort {}".format(str(wt), tf.get_cohort_coop(yas, wt)))

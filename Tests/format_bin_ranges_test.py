"""Function test for format_bin_ranges(bins, bin_labels)

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


bin_labels = [
    'Below Expectations',
    'Marginally Meets Expectations',
    'Meets Expectations',
    'Exceeds Expectations'
]

bins_standard = [0.0, 50.0, 60.0, 80.0, 100.0]
bins_engone = [0.0, 55.0, 60.0, 80.0, 100.0]
bins_coop = [0,2,3,4,5]

print("Bin ranges for standard")
print(tf.format_bin_ranges(bins_standard,bin_labels))

print("Bin ranges for Eng One")
print(tf.format_bin_ranges(bins_engone,bin_labels))

print("Bin ranges for Co-op")
print(tf.format_bin_ranges(bins_coop,bin_labels))

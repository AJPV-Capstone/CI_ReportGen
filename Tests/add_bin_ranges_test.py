"""Function test for format_bin_ranges(bins, bin_labels)"""

# Temp import for testing
import sys
sys.path.insert(0, '/Users/ryanletto/Desktop/WT2/CI_ReportGen')

import textformatting as tf


bin_labels = [
    'Below Expectations',
    'Marginally Meets Expectations',
    'Meets Expectations',
    'Exceeds Expectations'
]

bins_standard = [0.0, 50.0, 60.0, 80.0, 100.0]
bins_engone = [0.0, 55.0, 60.0, 80.0, 100.0]
bins_coop = [1,2,3,4,5]

print("Bin ranges for standard")
print(tf.format_bin_ranges(bins_standard,bin_labels))

print("Bin ranges for Eng One")
print(tf.format_bin_ranges(bins_engone,bin_labels))

print("Bin ranges for Co-op")
print(tf.format_bin_ranges(bins_coop,bin_labels))

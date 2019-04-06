"""Functions for formatting text in different ways"""
import textwrap
import re
import logging

def format_annotation_text(header_info):
    """Create a table-like format for the header text on a Report

    Args:
        header_info: A dictionary containing all of the elements that you want
            to show on the Report. The only required entry in the dictionary is
            "Graduate Attribute," the others are optional

    Returns:
        string: The 'labels' for the elements to graph, separated by HTML line
            breaks (<br>) that Plotly can use to create newlines in an annotation
        string: The 'descriptions' for the elements to graph, separated like the
            last string
        string: The Graduate Attribute is returned in a separate string so that
            its font size can be increased on a Report
    """
    logging.info("Cleaning up the header information and making it a table format")
    title = header_info["Graduate Attribute"]
    # After saving the element, set the GA attribute to empty for newline entry
    header_info["Graduate Attribute"] = " "

    label_list = list()
    description_list = list()

    for key in header_info.keys():
        logging.debug("Cleaning up %s", key)
        # Use textwrap to paragraphize the passed in text, with each line stored in a list
        label_list += textwrap.wrap(key + ':', width=12)
        description_list += textwrap.wrap(header_info[key], width=60)

        # If the number of lines in each list is not equal, add empty strings until they are equal
        difference = len(label_list) - len(description_list)
        if len(label_list) < len(description_list):
            [label_list.append(" ") for i in range (0, abs(difference))]
        elif len(description_list) < len(label_list):
            [description_list.append(" ") for i in range (0, abs(difference))]

    # Return strings separated by the <br> character and the GA
    return ('<br>'.join(label_list), '<br>'.join(description_list), title)


def format_percents(values):
    """Turn NumPy array values into list of percentage strings

    Args:
        values: a NumPy array (or other iterable) containing numbers

    Returns:
        list(str): A list of the numbers in percent format with no decimal places
    """
    formatted_percents = list()
    for percent in values:
        formatted_percents.append("{:.0f}%".format(percent))

    return formatted_percents


def format_bin_ranges(bins, bin_labels):
    """Format bins into a text description

    Currently, this does not format bin ranges properly for co-op data

    Args:
        bins(list(int)): A list of integers representing bin ranges.
        bin_labels(list(str)): A list of string titles for the bin categories.
            Uses the size of these bin labels to determine iteration

    Returns:
        string: A string describing the bin ranges
    """
    logging.info("Cleaning up the bin ranges and making them a message")
    size=len(bin_labels)
    logging.debug("Bin labels length is %s", size)

    bin_description = "Bin ranges: marks out of {:.0f}<br>".format(bins[size])
    # If the first bin is <=0, use a '<' sign to indicate the first bin
    if bins[0] <= 0:
        logging.debug("First bin was %s, adding a < sign", str(bins[0]))
        bin_description += "<{:.0f}: {}   ".format(bins[0],bin_labels[0])
    else:
        bin_description += "{:.0f}-{:.0f}: {}   ".format(bins[0],bins[1]-1,bin_labels[0])

    # Until the last bin, loop the string generation
    for i in range(1, size-1):
        bin_description += "{:.0f}-{:.0f}: {}   ".format(bins[i],bins[i+1]-1,bin_labels[i])
    # Add the last part of the bin label
    # Has to be done separately because of the -1 to the last bin in other cases
    bin_description += "{:.0f}-{:.0f}: {}".format(bins[size-1],bins[size],bin_labels[size-1])

    return bin_description


def get_cohort(year, course=None, term_taken=None):
    """Convert a year to equivalent cohort

    Args:
        year: a number containing year and optionally, semester (which will be ignored)
            Examples: 2017, 201703, 2019
        course: The course name or number
        term_taken: An override variable for courses that have unconventional
            numbering, such as CHEM1051 being taken in term 3.

    Returns:
        The equivalent cohort

    Exceptions:
        NotImplementedError: If the term_taken or the first number in the course
            name is 0, that means that the course is a work term course. This
            function does not have the necessary information to determine cohort
            using just the year, term taken and course number.
    """
    # Find the first number that occurs in the course UNLESS the term_taken
    # variable is used
    if not term_taken:
        term_taken = int(re.search("\d", course).group(0))

    # If term is included, split the year off of it via repeated int division
    # If year is greater than 9999, then it's not a year
    while year > 9999:
        year //= 10

    # Co-op work term check - raise error if the course found is a co-op course
    if term_taken == 0:
        raise NotImplementedError()

    cohort = year
    # Use conditionals to map the term to the cohort
    if term_taken in (1,2): # Engineering One usually - add 5
        cohort += 5
    elif term_taken in (3,4):# Year 2 of the program - add 4
        cohort += 4
    elif term_taken == 5: # Year 3 of the program - add 3
        cohort += 3
    elif term_taken in (6,7):   # Year 4 of the program - add 2
        cohort += 2
    elif term_taken == 8: # Year 5 of the program - add 1
        cohort += 1

    return cohort

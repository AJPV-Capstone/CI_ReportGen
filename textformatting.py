"""Functions for formatting text in different ways"""
import textwrap
import re
import logging

def format_annotation_text(header_info, textwrap_lim=60, sep='<br>'):
    """Create a table-like format for the header text on a Report

    Args:
        header_info: A dictionary containing all of the elements that you want
            to show on the Report. The only required entry in the dictionary is
            "Graduate Attribute," the others are optional
        textwrap_lim: The character limit on text wrapping. Defaults to 60
        sep: The separator character for the output string. Defaults to '<br>'
            as required by Plotly

    Returns:
        string: The 'labels' for the elements to graph, separated by HTML line
            breaks (<br>) that Plotly can use to create newlines in an annotation
        string: The 'descriptions' for the elements to graph, separated like the
            last string
        string: The Graduate Attribute is returned in a separate string so that
            its font size can be increased on a Report
    """
    # Copy the header information, use pass by value
    header_info_copy = header_info.copy()
    logging.info("Cleaning up the header information and making it a table format")
    title = header_info_copy["Graduate Attribute"]
    # After saving the element, set the GA attribute to empty for newline entry
    header_info_copy["Graduate Attribute"] = " "

    label_list = list()
    description_list = list()

    for key in header_info_copy.keys():
        logging.debug("Cleaning up %s", key)
        # Use textwrap to paragraphize the passed in text, with each line stored in a list
        label_list += textwrap.wrap(key + ':', width=12)
        description_list += textwrap.wrap(header_info_copy[key], width=textwrap_lim)

        # If the number of lines in each list is not equal, add empty strings until they are
        difference = len(label_list) - len(description_list)
        if len(label_list) < len(description_list):
            [label_list.append(" ") for i in range (0, abs(difference))]
        elif len(description_list) < len(label_list):
            [description_list.append(" ") for i in range (0, abs(difference))]

    # Return strings separated by the separator character and the title
    return (sep.join(label_list), sep.join(description_list), title)


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

    Currently, this uses a fairly inelegant solution for formatting co-op bins.
    If the difference between the first and last bin is 1, then the function
    calls a different one and returns the results of that

    Args:
        bins(list(int)): A list of integers representing bin ranges. Expects
            to receive 5 numbers (i.e. [0, 55, 65, 80, 100])
        bin_labels(list(str)): A list of string titles for the bin categories.
            Uses the size of these bin labels to determine iteration

    Returns:
        string: A string describing the bin ranges
    """
    logging.info("Cleaning up the bin ranges and making them a message")
    size=len(bin_labels)
    logging.debug("Bin labels length is %s", size)

    if bins[len(bins)-1] - bins[len(bins)-2] == 1:
        logging.debug("Co-op bins detected, calling format_coop_bins")
        return format_coop_bins(bins, bin_labels)

    bin_description = "Bin ranges: marks out of {:.0f}<br>".format(bins[size])
    # If the first bin is <=0, use a '<' sign to indicate the first bin
    if bins[0] <= 0:
        logging.debug("First bin was %s, adding a < sign", str(bins[0]))
        bin_description += "<{:.0f}: {}   ".format(bins[1],bin_labels[0])
    else:
        bin_description += "{:.0f}-{:.0f}: {}   ".format(bins[0],bins[1]-1,bin_labels[0])

    # Until the last bin, loop the string generation
    for i in range(1, size-1):
        bin_description += "{:.0f}-{:.0f}: {}   ".format(bins[i],bins[i+1]-1,bin_labels[i])
    # Add the last part of the bin label
    # Has to be done separately because of the -1 to the last bin in other cases
    bin_description += "{:.0f}-{:.0f}: {}".format(bins[size-1],bins[size],bin_labels[size-1])

    return bin_description


def format_coop_bins(bins, bin_labels):
    """Co-op bin label formatting

    Co-op bins won't format like the standard formatting method. This function
    handles the co-op binning exceptions

    Args:
        bins: The bin ranges. They are probably [0,2,3,4,5] if this function was
            called, and the function will behave as if they were. This allows
            for validation down the road if the binning message shows up really
            weird and nonsensical on a histogram
        bin_labels: The labels for the bins

    Returns:
        string: A string describing the bin ranges
    """
    size = len(bin_labels)
    bin_description = "Bin ranges: marks out of 5<br>"
    # Put a < sign for the first bin
    bin_description += "<={:.0f}: {}   ".format(bins[1], bin_labels[0])
    # Do remaining bins as
    for i in range (1, size):
        bin_description += "{:.0f}: {}   ".format(bins[i+1], bin_labels[i])
    return bin_description

def get_cohort(year, course=None, term_taken=None):
    """Convert a year to equivalent cohort

    The function cannot determine cohort for a work term course (i.e. ENGI 001W),
    so it assumes that the column name passed to it is a cohort and will simply
    return the year value passed back to it.

    Args:
        year: a number containing year and optionally, semester (which will be ignored)
            Examples: 2017, 201703, 2019
        course: The course name or number
        term_taken: An override variable for courses that have unconventional
            numbering, such as CHEM1051 being taken in term 3.

    Returns:
        The equivalent cohort
    """
    # Ensure that the value is an int
    year = int(year)
    # If term_taken was not passed to the function, find it using the course number
    if term_taken == None:
        term_taken = int(re.search("\d", course).group(0))

    # If term is included, split the year off of it via repeated int division
    # If year is greater than 9999, then it's not a year
    while year > 9999:
        year //= 10

    # Unique check - returns year if the course found has term_offered = 0
    if term_taken == 0:
        return year

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


def get_cohort_coop(year_and_semester, WT):
    """Determine the cohort of a work term student

    On a given work term, there can be 2 possible cohorts, and these can be
    calculated. See the following example:

     year and semester  |            cohort (work term numbers)
    --------------------+---------------------------------------------------
    Fall 2017 (201701)  |   2020(1-3) and 2018(4)
    --------------------+---------------------------------------------------
    Winter 2018 (201702)|   2021(1-2) and 2019(3-4)
    --------------------+---------------------------------------------------
    Spring 2018 (201703)|   2022(1) and 2020(2-4)
    --------------------+---------------------------------------------------

    The first possible cohort is year + semester + 2. See below:
        2017 + 1 + 2 = 2020
        2017 + 2 + 2 = 2021
        2017 + 3 + 2 = 2022
    The second possible cohort in a semester is just year + semester, or the
    first possible cohort - 2.

    There is a relation between semester and work term number associated with
    a cohort. The semester indicates how many work terms belong to a cohort.
        - If the semester number is 1, work terms 1-3 map to the first cohort
        - If the semester number is 2, work terms 1-2 map to the first cohort
        - If the semester number is 3, work term 1 maps to the first cohort

    Args:
        year_and_semester: Academic year format for when the work term was
            taken (i.e. 201703)
        WT: Student work term number (from 1 to 4)

    Returns:
        The cohort of the student

    Exceptions:
        ValueError: Raised when the function does not receive a  WT value from
            1 to 4
    """

    # Split the year and semester into 2 separate values
    year = year_and_semester // 100
    semester = year_and_semester % 10

    # Get the first possible and second possible cohorts
    first_cohort = year + semester + 2

    WTs = [1, 2, 3, 4]  # Possible work terms
    if WT not in WTs:
        raise ValueError

    # Build a list of possible cohorts for the first semester
    first_cohort_WTs = [WTs[i] for i in range(0, 4-semester)]

    if WT in first_cohort_WTs:
        return first_cohort
    else:
        return first_cohort - 2

"""Functions for formatting text in different ways"""
import textwrap
import re

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
    title = header_info["Graduate Attribute"]
    # After saving the element, set the GA attribute to empty for newline entry
    header_info["Graduate Attribute"] = " "

    label_list = list()
    description_list = list()

    for key in header_info.keys():
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
    size=len(bin_labels)
    bin_description = "Bin ranges: marks out of {:.0f}<br>".format(bins[size])
    # If the first bin is <=0, use a '<' sign to indicate the first bin
    if bins[0] <= 0:
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


def get_cohort(x, course=None, term_taken=None):
    """Convert a year and term to equivalent cohort using course number

    Args:
        x: a number containing year and optionally, semester
            Examples: 2017, 201703, 2019
        course: The course name or number
        term_taken: An override variable for courses that have unconventional
            numbering, such as CHEM1051 being taken in term 3. Overrides any
            derivations

    Returns:
        The equivalent cohort

    Exceptions:
        NotImplementedError: If the term_taken or the first number in the course
            name is 0, that means that the course is a work term course. This
            function does not have the necessary information to determine cohort
            using just the year, semester and course number.
    """
    # Find the first number that occurs in the course UNLESS the term_taken
    # variable is used
    if not term_taken:
        term_taken = int(re.search("\d", course).group(0))

    # Convert x to a string so that it's easier to deal with
    x = str(x)
    # If term is included, split the year and semester
    if len(x) > 4:
        year = int(x[:4])
        semester = int(x[5:])
    else:
        year = int(x)
        semester = 0

    # Co-op work term check - raise error if the course found is a co-op course
    if term_taken == 0:
        raise NotImplementedError()

    # Start with cohort equalling the year. If the course was taken in the winter
    # or summer, add 1
    cohort = year
    if semester > 1:
        cohort += 1

    # Use conditionals from that point
    if term_taken in (1,2): # 20(y)01 or 20(y)02
        cohort += 5
    elif term_taken in (3,4):# 20(y+1)01 or 20(y+1)03
        cohort += 4
    elif term_taken == 5: # 20(y+2)02
        cohort += 3
    elif term_taken in (6,7):   # 20(y+3)01 or 20(y+4)03
        cohort += 2
    elif term_taken == 8: # 20(y+4)02
        cohort += 1

    return cohort

"""Regenerates default.json that the ReportConfig class requires to run

Report Attributes:
    annotation_font: The font size of the annotations. All other font sizes
        are derived from this font size
    dpi: The dots per inch of the generated Report. Default is 150
    orientation: The plot orientation. The current choices are 'landscape'
        and 'portrait.' The 'portrait' orientation might not work properly,
        and the program defaults to 'landscape'
    format: The save format for the Report. Defaults to 'pdf,' but any
        file extension supported by Plotly's Static Image Export should
        work.

Histogram Attributes:
    max_plots(int): The maximum number of plots that can be on a Report's
        histogram at once. Defaults to 5
    add_percents(bool): Show bar percentages (Default True)
    add_legend(bool): Show legend (Default True)
    show_NDA(bool): Indicates whether or not a 'No Data Available' bin
        should appear on some plots. The condition for this bin is
        specified with NDA_threshold
    NDA_threshold(float): If the amount of no data entries is greater
        than or equal to this threshold value, the 'No Data Available'
        bin will appear for ALL plots. Defaults to 0.10, or 10%

Indicator Parsing Attributes:
    indsheet_query_cols(str): A comma-separated list of the indicator
        sheet column names to query
"""

import json
import os

default = {
    "name": "default",
    "plot_grades_by": "year",
    "annotation_font": 16,
    "dpi": 150,
    "orientation": "landscape",
    "format": "pdf",
    "max_plots": 5,
    "add_title": True,
    "add_percents": True,
    "add_legend": True,
    "add_bin_ranges": True,
    "show_NDA": True,
    "NDA_threshold": 0.1,
    "header_attribs": "Graduate Attribute, Indicator, Level, Program, Course, Assessment",
    "header_xloc": 0.33,
    "header_yloc": 1.9,
    "graph_title": "GRADE DISTRIBUTION",
    "textwrap_lim": 72,
    "grade_backup_dirs": "Core, Co-op, ECE"
}

f = open('../config/default.json', 'w+')
f.write(json.dumps(default, indent=4))
print("default.json generated successfully")

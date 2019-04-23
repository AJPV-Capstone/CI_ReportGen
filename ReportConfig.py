import json
import base64
import os
import logging


class ReportConfig(object):
    """Report options/configurations

        A class that stores parameters used for various automations in a Report
        object. This class allows JSON loading so that popular templates can
        be saved and re-used. Also opens the MUN logo and keeps it open so that
        during Report autogeneration, it does not have to be closed and
        re-opened many times. The JSON configurations load last, so they can be
        used to override any attributes set in the object.

        Attributes from config file:
            name: The name of the configuration
            plot_grades_by: A parameter meant to indicate how to plot grades.
                Currently, the project only does plotting by year, but the
                intended plan was to set up the report generator such that it
                could plot grades from multiple course files on one graph.
            annotation_font: The font size of the annotations. All other font sizes
                are derived from this font size. Default size is 16
            dpi: The dots per inch of the generated Report. Default is 150
            orientation: The plot orientation. The current choices are 'landscape'
                and 'portrait.' The 'portrait' orientation might not work properly,
                and the program defaults to 'landscape'
            format: The save format for the Report. Defaults to 'pdf,' but any
                file extension supported by Plotly's Static Image Export should
                work.

            max_plots(int): The maximum number of plots that can be on a Report's
                histogram at once. Defaults to 5
            add_title(bool): Add a graph title (Default True)
            graph_title(str): The title that should be added to the graph. Can
                be a formatted string and the generator will automatically try
                to put cohort in it. Defaults to "GRADE DISTRIBUTION"
            add_percents(bool): Show bar percentages (Default True)
            add_legend(bool): Show legend (Default True)
            add_bin_ranges(bool): Add the bin range description (Default True)
            show_NDA(bool): Indicates whether or not a 'No Data Available' bin
                should appear on some plots. The condition for this bin is
                specified with NDA_threshold
            NDA_threshold(float): If the percentage of no data entries is greater
                than or equal to this threshold value, the 'No Data Available'
                bin will appear for ALL plots. Defaults to 0.10, or 10%

            header_attribs: A comma-separated string of the things that should
                be added to a graph header
            header_xloc: The x location of the header
            header_yloc: The y location of the header
            textwrap_lim: The limit on textwrap for the header. Defaults to 72
                characters

        Other Attributes (not from config files):
            MUN_logo: The MUN logo in base64
            font_sizes: A dictionary of font sizes used in the Report
            paper_dimensions: A dictionary of tuples indicating paper dimensions
            indicators_loc: Where the program can find the indicator master sheets
            grades_loc: Where the program can find grades files
            histograms_loc: Where the program should save histograms

        Todo:
            - Verify the accuracy of this docstring
            - Implement a config saving feature using this object
    """


    def __init__(self, config_file = None, config_path=None):
        """Object initializes from configuration file

        Object also opens the MUN logo

        Args:
            config_file(string): A configuration to use. Defaults to using just
                the default configuration
            config_path: The path to the config folders. Defaults to finding it
                with os.path
        """
        logging.info("Start of ReportConfig initialization")
        if not config_path:
            config_path = os.path.dirname(__file__) + '/config'
            logging.debug("Config path not specified, using %s", config_path)

        logging.info("Setting up paper dimensions")
        self.paper_dimensions = {
            'landscape': (11.69, 8.27),
            'portrait': (8.27, 11.69)
        }
        # Open the MUN logo and save it in base64
        logging.info("Saving MUN logo in base64")
        logging.debug("Opening MUN logo from %s", os.path.dirname(__file__) + '/MUN_Logo_RGB2.png')
        with open(os.path.dirname(__file__) + '/MUN_Logo_RGB2.png', 'rb') as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode()
        self.MUN_logo = 'data:image/png;base64,' + encoded_logo

        # Set up paths to directories
        logging.info("Setting default directories to find indicators, grades and histograms")
        self.indicators_loc = os.path.dirname(__file__) + '/../Indicators'
        self.grades_loc = os.path.dirname(__file__) + '/../Grades'
        self.histograms_loc = os.path.dirname(__file__) + '/../Histograms'

        # Load default config file and set attributes based on its contents
        logging.info("Setting attributes from default.json")
        default = json.load(open(config_path + '/' + 'default.json'))
        for key in default:
            setattr(self, key, default[key])

        # Overwrite default options with the passed in config file if necessary
        if config_file:
            new_attribs = json.load(open(config_path + '/' + config_file))
            logging.info("Overriding attributes using config file %s", config_file)
            for key in new_attribs:
                setattr(self, key, new_attribs[key])

        # Set up font sizes and paper dimensions
        logging.info("Setting up font sizes")
        self.font_sizes = {
            'graph_title': self.annotation_font*1.2,
            'yaxis_title': self.annotation_font,
            'GA_text': self.annotation_font*1.5,
            'annotations': self.annotation_font,
            'axis_labels': int(self.annotation_font/1.2),
            'barcounts': int(self.annotation_font/1.2),
            'legend_text': self.annotation_font
        }

        logging.info("ReportConfig initialization complete!")

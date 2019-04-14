import plotly.graph_objs as go
import plotly.io as pio
import textformatting as tf
import plotly_object_generation as pog
from ReportConfig import ReportConfig
import os
from collections import defaultdict
import numpy as np
import logging
import pandas as pd

class Report(object):
    """Report Class

    Used for generating reports on indicator data. Uses plotly to generate
    histograms. Many attributes that define properties about the plot are
    stored in a ReportConfig object that this one has reference to. For more
    information, see the ReportConfig docstring. For the most part, this object
    assumes that input data has already been validated.

    Attributes:
        config: A ReportConfig object
        layout: A plotly.Layout that generates from certain attributes in
            ReportConfig
        indicator_data: A dictionary containing any information needed on a
            histogram header. The dictionary needs to at least contain
            "Graduate Attribute" as one of its keys, but other than that,
            the keys are optional
        bins: The bin range for this assessment to use. Should be a 4-digit
            list if the bottom bin restriction is 0. If the bins are passed as
            5-digit, then the first one will be used as the lowest bin
        _annotations: A list of plotly.layout.Annotation objects that the object
            uses when the Report is built into a Figure
    """


    def __init__(self, indicator_data, bins, config = None):
        """Object initialization

        Args:
            indicator_data: A dictionary containing GA, Indicator, Level,
                Program, Course, and Assessment
            bins: A list of floats containing bin ranges
            config: a ReportConfig object reference that the object uses
                to configure various parameters. Uses a default config if
                none is passed as an argument

        Todo:
            - Write this docstring
        """
        logging.info("Initializing Report object")
        logging.debug("Report being initialized with bins: %s", bins)
        logging.debug("Report being initialized with indicator data: %s", indicator_data)
        # If no config was passed as an argument, create a new one
        if not config:
            logging.info("No config was passed to the object, creating one now")
            self.config = ReportConfig()
        else:
            logging.info("Config was passed to the object")
            self.config = config

        # Set the indicator data and bin things
        self.indicator_data = indicator_data
        # Append 0 to the bins front if the size is 4
        if len(bins) == 4:
            self.bins = [0] + bins
            logging.debug("Indicator bins were turned into: %s", ', '.join(str(x) for x in self.bins))
        else:
            self.bins = bins

        self.bin_labels = [
            'Below Expectations',
            'Marginally Meets Expectations',
            'Meets Expectations',
            'Exceeds Expectations'
        ]

        logging.debug("Indicator bins: %s", ', '.join(str(x) for x in self.bins))
        logging.debug("Indicator data: %s", str(self.indicator_data))

        # Set up the plotly objects
        logging.info("Setting up plotly things, including a list of traces, a list of annotations, and a layout")
        self.traces=list()
        self.layout=pog.generate_layout(self.config)
        self._annotations = list()

        logging.info("Report object initialization complete!")


    def plot(self, grades):
        """Plot the stored assessment

        Args:
            grades: A pandas DataFrame storing the grades that need to be plotted.
                The program will use the column names of the DataFrame as the legend
                entries

        Todo:
            - Clean up the NDA filtering thing (idea: do the threshold check in
              the np.histogram for loop)
        """
        logging.info("Setting up required resources for plotting")
        # Store the data in dicts of NumPy arrays before converting to barcharts
        data = defaultdict()
        # Copy the bin ranges
        bins_copy = self.bins.copy()

        # If the difference between the last 2 bins is 1, assume that these are
        # co-op bins. If so, add 1 to each bin so that NumPy's histogram will
        # work properly.
        if bins_copy[len(bins_copy)-1] - bins_copy[len(bins_copy)-2] == 1:
            for i in range (1, len(bins_copy)):
                bins_copy[i] += 1

        # Also copy the bin labels
        bin_labels_copy = self.bin_labels.copy()

        # if show_NDA is True, add -1 to the front of the bins
        if self.config.show_NDA == True:
            logging.info("Show NDA is set to True, adding -1 to front of bins")
            bins_copy = [-1.0] + bins_copy
        logging.debug("Bins being passed to NumPy histogram: %s", ', '.join(str(x) for x in bins_copy))

        # Histogram data by column
        for col in grades.columns:
            # Determine the cohort size by removing the null values from the column
            # that Pandas has to put there. The resulting list's length is used
            data_to_histogram = list()
            for x in grades[col]:
                if not pd.isnull(x):
                    data_to_histogram.append(x)
                # Raise an error if the value is a string type because NumPy will
                # just complain anyways
                if isinstance(x, type('string')):
                    error = "A value in the {} grades for {} {} is not a number. Please fix and try again.".format(
                        self.indicator_data['Program'],
                        self.indicator_data['Course'],
                        self.indicator_data['Assessment']
                    )
                    raise ValueError(error)
            cohort_size = len(data_to_histogram)
            # Add histogrammed grades to the data dict, converted to percentage
            logging.info("Running NumPy histogram")
            data[col] = np.histogram(data_to_histogram, bins=bins_copy)[0] / cohort_size * 100
            logging.debug("Data added to data[%s]:", col)
            logging.debug(', '.join(str(x) for x in data[col]))
            logging.debug('bins are %s', ', '.join(str(x) for x in bins_copy))

        # Check the NDA percentages and determine if NDA should be shown
        logging.info("Checking to see if NDA should be removed")
        if self.config.show_NDA == True:
            logging.info("Show NDA is True, so check is going ahead. NDA threshold: %s", str(self.config.NDA_threshold))
            delete_NDA = True
            # First pass determines if any of the bins are above the threshold
            logging.info("Performing first pass over data to check if any bins are above threshold")
            for key in data.keys():
                # If any NDA bins are above the threshold, don't delete them
                if data[key][0] >= self.config.NDA_threshold*100:
                    delete_NDA = False
                    logging.debug("The NDA value from key %s exceeded the threshold, so NDA will not be stripped", key)
                    logging.debug("That value was %s", str(data[key][0]))
                    # Add NDA bin label to front
                    bin_labels_copy = ["No Data Available"] + bin_labels_copy
                    break

            if delete_NDA == True:
                logging.info("No value exceeded the threshold, so NDA bins will be stripped")
                # Second pass will remove the NDA bins if they have to be removed
                for key in data.keys():
                    data[key] = np.delete(data[key], 0)

        # Bar the data
        logging.info("Barring the data now")
        logging.debug("Bin labels being passed to plotly bar: %s", ', '.join(bin_labels_copy))
        for key in data.keys():
            # Add percentage text labels only if add_percents is True
            logging.debug("Barring data for set %s", key)
            if not self.config.add_percents:
                logging.debug("self.config.add_percents is %s, bar text set to None", str(self.config.add_percents))
                text = None
            else:
                logging.debug("self.config.add_percents is %s, setting bar text to percentages", str(self.config.add_percents))
                text = tf.format_percents(data[key])

            logging.debug("Adding the plotly bar trace now")
            self.traces.append(go.Bar(
                name = key,
                x = bin_labels_copy, y = data[key],
                text = text,
                textposition = 'auto',
                constraintext = 'inside',
                textfont=dict(size=int(self.config.font_sizes['barcounts']/100*self.config.dpi))
            ))

        logging.info("Barring complete!")


    def _append_annotations(self):
        """Append annotations to self.layout.annotations

        This method was originally created to try and fix a nonexistent workaround.
        However, since there was no need to make a workaround, this method is
        pretty redundant now, but it's staying here anyways for the time being

        """
        logging.debug("Updating the annotations in the layout using self._annotations")
        self.layout.update(annotations=self._annotations)


    def add_header(self):
        """Add the header information to the annotations list"""
        # Get the text to add to the graph
        logging.info("Adding header to Report")
        labels, descriptions, title = tf.format_annotation_text(self.indicator_data, self.config.textwrap_lim)
        self._annotations += [
            # GA
            go.layout.Annotation(
                x=self.config.header_xloc, y=self.config.header_yloc,
                showarrow=False,
                text=title,
                xref='paper', yref='paper',
                xanchor='left',
                align = 'left',
                font = dict(size=int(self.config.font_sizes['GA_text']/100*self.config.dpi))
            ),
            # Indicator Descriptions
            go.layout.Annotation(
                x=self.config.header_xloc, y=self.config.header_yloc,
                showarrow=False,
                text=descriptions,
                xref='paper', yref='paper',
                xanchor='left',
                align = 'left',
                font = dict(size=int(self.config.font_sizes['annotations']/100*self.config.dpi))
            ),
            # Indicator Label Column Thing (the catagories)
            go.layout.Annotation(
                x=self.config.header_xloc - 0.02, y=self.config.header_yloc,
                showarrow=False,
                text=labels,
                xref='paper', yref='paper',
                xanchor='right',
                align = 'left',
                font = dict(size=int(self.config.font_sizes['annotations']/100*self.config.dpi))
            )
        ]


    def add_bin_ranges(self):
        """Add bin ranges to bottom of plot"""
        logging.info("Adding bin ranges to Report")
        self._annotations.append(go.layout.Annotation(
            x=0.5, y=-self.config.font_sizes['legend_text']/100*1.7,
            showarrow=False,
            xref='paper',yref='paper',
            xanchor='center', yanchor='bottom',
            align = 'left',
            font=dict(size=int(self.config.font_sizes['annotations']/100*self.config.dpi)),
            text=tf.format_bin_ranges(self.bins, self.bin_labels)
            )
        )


    def add_title(self, cohort=""):
        """Add graph title to the Report

        Args:
            cohort: The cohort to add to the title, assuming that the title
                string in the ReportConfig is a formatted string. Defaults
                to empty
        """
        logging.info("Adding title to graph on the Report")
        self._annotations.append(go.layout.Annotation(
            x=0.5, y=1+self.config.font_sizes['graph_title']/125,
            showarrow=False,
            text=self.config.graph_title.format(cohort),
            xref='paper',yref='paper',
            xanchor='center',
            font=dict(size=int(self.config.font_sizes['graph_title']/100*self.config.dpi))
            )
        )

    def save(self, savename, format=None):
        """Save Report object

        Args:
            savename: Save file name
            format: The file format to save to. Uses whatever config uses by default
        """
        if not format:
            format = self.config.format

        logging.info("Saving Report in %s format", format)
        # Add the annotations to the figure Layout
        self._append_annotations()
        fig = go.Figure(data = self.traces, layout = self.layout)
        # Console print to show that the program is still running
        print("Saving", savename)
        pio.write_image(fig, savename, format)

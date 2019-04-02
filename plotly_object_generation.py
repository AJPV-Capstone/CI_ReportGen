"""Functions to generate certain plotly objects for the Report"""
import plotly.graph_objs as go

def generate_layout(config):
    """Generate Layout object

    Args:
        config: A ReportConfig object

    Returns:
        layout: A partially-completed plotly layout
    """
    # Set up certain layout elements based on config parameters
    margin = go.layout.Margin(
        # Large top margin for header information
        t=int(config.paper_dimensions[config.orientation][1]*config.dpi/2.3),
        # Smaller left and right margins
        l=int(config.paper_dimensions[config.orientation][0]*config.dpi*1.5/config.font_sizes['yaxis_title']),
        r=int(config.paper_dimensions[config.orientation][0]*config.dpi*1.5/config.font_sizes['yaxis_title'])
    )

    # If a legend is added, make sure there is enough space on bottom margin to show it
    if config.add_legend == True:
        margin.b=int(config.paper_dimensions[config.orientation][1]*config.dpi*config.font_sizes['legend_text']/100)

    # Some layout stuff to initialize
    layout=go.Layout(
        autosize = False,
        # Width and height (in pixels) determined by paper orientation and DPI
        width = int(config.paper_dimensions[config.orientation][0]*config.dpi),
        height = int(config.paper_dimensions[config.orientation][1]*config.dpi),
        # Global font for the layout defined by annotation font size
        font = dict(size=int(config.annotation_font/100*config.dpi)),
        # Add MUN logo to the top left-hand corner
        images =[dict(
            source = config.MUN_logo,
            xref = "paper", yref = "paper",
            x = -0.05, y = 1.9,
            sizex = 0.35, sizey = 0.35
        )],
        margin = margin,
        barmode = 'group',
        # Set axes fonts to be relatively small and set y axis range to 0-100
        xaxis = dict(
            tickfont=dict(size=int(config.font_sizes['axis_labels']/100*config.dpi))
        ),
        yaxis = dict(
            title="% OF CLASS",
            titlefont=dict(size=int(config.font_sizes['yaxis_title']/100*config.dpi)),
            tickfont=dict(size=int(config.font_sizes['axis_labels']/100*config.dpi)),
            range=(0,100),
            nticks=10
        ),
        # Show legend dependent on the config option
        showlegend = config.add_legend,
        # Legend positioning (if it's shown at all)
        legend=dict(
            orientation = 'h',
            xanchor = 'center', yanchor = 'bottom',
            x= 0.5, y = -config.font_sizes['legend_text']/100,
            font = dict(size=int(config.font_sizes['legend_text']/100*config.dpi))
        )
    )
    return layout

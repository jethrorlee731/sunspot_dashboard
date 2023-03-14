"""
Jethro R. Lee
DS 3500
Homework 2 - sunspot_dashboard.py: Creating a dashboard for tracking and scrutinizing past and trending sunspot activity
February 5, 2023
"""

from dash import Dash, dcc, html, Input, Output
from copy import copy
import plotly.express as px
import sunspot as ss

# create the layout
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        # adds a header to the dashboard
        html.H2('Interactive International Sunspot Number Dashboard'),

        # determines the sun image shown on the dashboard
        html.P('Select a filter for the sun image:'),

        html.Div([
            dcc.Dropdown(id='img_filter', options=['EIT 171', 'EIT 195', 'EIT 284', 'EIT 304', 'SDO/HMI Continuum',
                                                   'SDO/HMI Magnetogram', 'LASCO C2', 'LASCO C3'],
                         value='SDO/HMI Continuum',
                         clearable=False)]),

        html.Img(id='sun_image', style={'height': '15%', 'width': '15%'}),

    ], style={'textAlign': 'center'}),

    html.Div([
        # displays a plot showing the sunspot counts over a user-specified range of years
        dcc.Graph(id='sunspot_count', style={'width': '45vw', 'height': '45vh'}),

        # allows the user to define the unit of the observation periods
        html.P('Select the Unit of Observation Periods:'),
        dcc.Dropdown(id='obs_periods', options=['Days', 'Months'], value='Days', clearable=False),

        # allows the user to control the amount of smoothing in the smoothed plot
        html.P('Choose the number of observation periods (in the same unit chosen above) to smooth the data over'),
        dcc.Slider(id='smoothing_degree', min=0, max=50, step=1, value=0, marks=None,
                   tooltip={'placement': 'bottom', 'always_visible': True}),

        # displays a plot showing the average sunspot counts per year
        dcc.Graph(id='sunspot_yearly_avg', style={'width': '50vw', 'height': '45vh'}),

        # allows a user to control whether error bars are incorporated into the charts
        html.P('Show error bars?'),
        dcc.Dropdown(id='error_bars', options=['Yes', 'No'], value='No', clearable=False)
    ], style={'width': '49%', 'display': 'inline-block'}),

    html.Div([
        # allows the user to control the range of years represented in the three plots
        html.P('Select a range of years:'),
        dcc.RangeSlider(id='year_range', min=1818, max=2022, step=1, value=[1818, 2022],
                        marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),

        # allows the user to only be shown data from a particular range of months
        html.P('Observe data from a range of months:'),
        dcc.RangeSlider(id='month_range', min=1, max=12, step=1, value=[1, 12], marks={1: 'January', 2: 'February',
                                                                                       3: 'March', 4: 'April',
                                                                                       5: 'May',
                                                                                       6: 'June', 7: 'July',
                                                                                       8: 'August',
                                                                                       9: 'September',
                                                                                       10: 'October',
                                                                                       11: 'November',
                                                                                       12: 'December'}),

        # allows the user to only be shown data from a particular range of dates
        html.P(
            'Observe data from a particular range of dates in the month chosen above (you must specify the '
            'observation period unit to be days for changes to be applied)'),
        dcc.RangeSlider(id='day_range', min=1, max=31, step=1, value=[1, 31],
                        marks=None, tooltip={'placement': 'bottom', 'always_visible': True}),

        # displays a plot portraying the variability of the sunspot cycle, which gets specified by the user
        dcc.Graph(id='variability', style={'width': '45vw', 'height': '45vh'}),

        # allows the user to adjust the cycle period on the variability plot
        html.P('Tune the cycle period (Years)'),
        dcc.Slider(id='cycle_period_years', min=8, max=14, step=1, value=11),
        html.P('Add months to the cycle period'),
        dcc.Slider(id='cycle_period_months', min=0, max=11, step=1, value=0),
        html.P('Add days to the cycle period'),
        dcc.Slider(id='cycle_period_days', min=0, max=30, step=1, value=0)

    ], style={'width': '45%', 'display': 'inline-block', 'textAlign': 'center'}),

])


# define the callback
@app.callback(
    Output('sun_image', 'src'),
    Input('img_filter', 'value'),
)
def display_sun_image(img_filter):
    """ Determines which filtered current real-time sun image gets displayed on the dashboard

        Args:
            img_filter (str): the filter applied to the sun image shown on the dashboard

        Returns:
            src (str): a direct link to the appropriate jpg image shown on the dashboard
    """

    # Retrieves the link to the sun image with the user-specified filter
    if img_filter == 'EIT 171':
        src = 'https://soho.nascom.nasa.gov/data/realtime/eit_171/1024/latest.jpg'
    elif img_filter == 'EIT 195':
        src = 'https://soho.nascom.nasa.gov/data/realtime/eit_195/1024/latest.jpg'
    elif img_filter == 'EIT 284':
        src = 'https://soho.nascom.nasa.gov/data/realtime/eit_284/1024/latest.jpg'
    elif img_filter == 'EIT 304':
        src = 'https://soho.nascom.nasa.gov/data/realtime/eit_304/1024/latest.jpg'
    elif img_filter == 'SDO/HMI Continuum':
        src = 'https://soho.nascom.nasa.gov/data/realtime/hmi_igr/1024/latest.jpg'
    elif img_filter == 'SDO/HMI Magnetogram':
        src = 'https://soho.nascom.nasa.gov/data/realtime/hmi_mag/1024/latest.jpg'
    elif img_filter == 'LASCO C2':
        src = 'https://soho.nascom.nasa.gov/data/realtime/c2/1024/latest.jpg'
    elif img_filter == 'LASCO C3':
        src = 'https://soho.nascom.nasa.gov/data/realtime/c3/1024/latest.jpg'

    return src


# define the callback
@app.callback(
    Output('sunspot_count', 'figure'),
    Input('obs_periods', 'value'),
    Input('smoothing_degree', 'value'),
    Input('year_range', 'value'),
    Input('month_range', 'value'),
    Input('day_range', 'value'),
    Input('error_bars', 'value'),
)
def plot_sunspot_counts(obs_periods, smoothing_degree, year_range, month_range, day_range, error_bars):
    """ Creates two plots (non-smooth and smooth) to portray the sunspot counts over a period of time

        Args:
            obs_periods (str): user-defined unit of observation periods (months or days)
            smoothing_degree (int): controls the extent to which the sunspot dataframe gets smoothed for another plot
            year_range (list of ints): year_range[0] contains the min year represented on the plot, while year_range[1]
                                       specifies the max
            month_range (list): month_range[0] contains the min month represented on the plot, while month_range[1]
                                specifies the max
            day_range (list): day_range[0] contains the min date in a month represented on the plot, while day_range[1]
                              specifies the max
            error_bars (str): indicates whether error bars are added to the line charts

        Returns:
            fig (px.line): a line chart displaying sunspot counts over a user specified-range stacked by a smoothed line
                           showing average values over a number of observation periods specified by the user
    """
    # Read sunspot data
    df_sunspot_activity = ss.read_sunspot(obs_periods)
    df_sunspot_activity = ss.clean_sunspot_data(df_sunspot_activity, year_range, month_range, day_range, obs_periods)

    # Retrieve smooth sunspot data
    df_sunspot_smooth = copy(df_sunspot_activity)
    df_sunspot_smooth['Rolling_Avg'] = df_sunspot_smooth['Mean_Obs'].rolling(smoothing_degree).mean()

    if error_bars == 'Yes':
        # Generate sunspot count plot with error bars
        fig = px.line(df_sunspot_activity, x='Year', y='Mean_Obs', error_y='Standard_Deviation',
                      labels={'Mean_Obs': 'Sunspot Number'},
                      title='International Sunspot Number: Monthly and Smoothed')

        # Generate smooth sunspot count plot with error bars
        df_sunspot_smooth['Standard_Deviation'] = df_sunspot_smooth['Rolling_Avg'].std()
        fig.add_traces(
            list(px.line(df_sunspot_smooth, x='Year', y='Rolling_Avg', error_y='Standard_Deviation',
                         labels={'Mean_Obs': 'Sunspot Number'},
                         title='International Sunspot Number').select_traces()))

    else:
        # Generate sunspot count plot without error bars
        fig = px.line(df_sunspot_activity, x='Year', y='Mean_Obs', labels={'Mean_Obs': 'Sunspot Number'},
                      title='International Sunspot Number')

        # Generate smooth sunspot count plot without error bars
        fig.add_traces(
            list(px.line(df_sunspot_smooth, x='Year', y='Rolling_Avg',
                         labels={'Mean_Obs': 'Sunspot Number'},
                         title='International Sunspot Number: Monthly and Smoothed').select_traces()))

    # Determining the proper label for the non-smooth sunspot plot
    if obs_periods == 'Days':
        sunspot_label = 'Daily'
    else:
        sunspot_label = 'Monthly'

    # Adding labels to the monthly/daily and smooth sunspot lines and coloring the smooth data red
    fig['data'][0]['name'] = sunspot_label
    fig['data'][1]['name'] = 'Smoothed'
    fig['data'][1]['line']['color'] = 'red'

    # Adding a legend to the line chart
    fig.update_traces(showlegend=True)

    return fig


# define the callback
@app.callback(
    Output('sunspot_yearly_avg', 'figure'),
    Input('obs_periods', 'value'),
    Input('year_range', 'value'),
    Input('month_range', 'value'),
    Input('day_range', 'value'),
    Input('error_bars', 'value'),
)
def plot_sunspot_yearly_avg(obs_periods, year_range, month_range, day_range, error_bars):
    """ Creates a bar chart to portray the average sunspot counts per year

        Args:
            obs_periods (str): user-defined unit of observation periods (months or days)
            year_range (list of ints): year_range[0] contains the min yr represented on the chart, while year_range[1]
                                       specifies the max
            month_range (list): month_range[0] contains the min month represented on the chart, while month_range[1]
                                specifies the max
            day_range (list): day_range[0] contains the min date in a month represented on the chart, while day_range[1]
                              specifies the max
            error_bars (str): indicates whether error bars are added to the bar chart or not

        Returns:
            fig (px.bar): a bar chart displaying sunspot yearly averages over a user specified-range
    """
    # Read sunspot data
    df_sunspot_activity = ss.read_sunspot(obs_periods)
    df_sunspot_activity = ss.clean_sunspot_data(df_sunspot_activity, year_range, month_range, day_range, obs_periods)
    df_sunspot_yearly_avg = df_sunspot_activity.groupby(['Year']).mean().reset_index('Year')

    if error_bars == 'Yes':
        df_sunspot_yearly_avg['Standard_Deviation'] = df_sunspot_yearly_avg['Mean_Obs'].std()
        # Generate sunspot yearly average plot with error bars
        fig = px.bar(df_sunspot_yearly_avg, x='Year', y='Mean_Obs', error_y='Standard_Deviation',
                     labels={'Mean_Obs': 'Average Sunspot Number'})

    else:
        # Generate sunspot yearly average plot without error bars
        fig = px.bar(df_sunspot_yearly_avg, x='Year', y='Mean_Obs', labels={'Mean_Obs': 'Average Sunspot Number'},
                     title='Average Sunspot Count Per Year')

    return fig


# define the callback
@app.callback(
    Output('variability', 'figure'),
    Input('obs_periods', 'value'),
    Input('year_range', 'value'),
    Input('month_range', 'value'),
    Input('day_range', 'value'),
    Input('cycle_period_years', 'value'),
    Input('cycle_period_months', 'value'),
    Input('cycle_period_days', 'value'),
)
def plot_sunspot_variability(obs_periods, year_range, month_range, day_range, cycle_period_years,
                             cycle_period_months, cycle_period_days):
    """ Generates a plot that visualizes the variability of the sunspot cycle

        If the user inputs a cycle length period close to the actual period, then the scatter plot should demonstrate
        less variability among the data.

        Args:
            obs_periods (str): user-defined number of observation periods (months or days)
            year_range (list of ints): year_range[0] contains the min yr a row represented on the plot, while
                                       year_range[1] specifies the max
            month_range (list): month_range[0] contains the min month represented on the plot, while month_range[1]
                                specifies the max
            day_range (list): day_range[0] contains the min date in a month represented on the plot, while day_range[1]
                              specifies the max
            cycle_period_years (int): user-defined  numbers of years of a cycling period, of which its variability is
                                      shown in a scatter plot
            cycle_period_months (int): user-specified additional months to the cycling period
            cycle_period_days (int): user-defined additional days to the cycling period

        Returns:
            fig (px.scatter): a scatter plot that displays the variability of the sunspot cycle.
    """
    # Read sunspot data
    df_sunspot_activity = ss.read_sunspot(obs_periods)
    df_sunspot_activity = ss.clean_sunspot_data(df_sunspot_activity, year_range, month_range, day_range)

    # Change the data so that it represents each cycle overlaying upon itself
    cycle_period = cycle_period_years + (cycle_period_months / 12) + (cycle_period_days / 365.25)
    df_sunspot_activity['Decimal_Date'] = df_sunspot_activity['Decimal_Date'] % cycle_period

    # Plots only instances in which a positive number of sunspots was observed
    df_sunspot_activity = df_sunspot_activity[df_sunspot_activity['Mean_Obs'] > 0]

    # Generate the variability plot
    fig = px.scatter(df_sunspot_activity, x='Decimal_Date', y='Mean_Obs', labels={'Decimal_Date': 'Years',
                                                                                  'Mean_Obs': '# of Sunspots'},
                     title='Sunspot Cycle: ' + str(cycle_period), opacity=0.5)

    return fig


def main():
    # runs the server
    app.run_server(debug=True)


if __name__ == '__main__':
    main()

"""
Jethro R. Lee
DS 3500
Homework 2 - sunspot.py: Enables a user to read and clean a data file with information on sunspots from the SIDC
February 5, 2023
"""

import pandas as pd


def read_sunspot(obs_periods=None):
    """ Reads the sunspot file and transforms its contents into a dataframe

        Args:
            obs_periods (str): user-defined number of observation periods (months or days)

        Returns:
            sunspot (pd.DataFrame): a dataframe that organizes sunspot data from 1749 to 2022
    """
    if obs_periods == 'Days':
        sunspot = pd.read_csv('SN_d_tot_V2.0.csv', header=0, delimiter=';')
        sunspot.columns = ['Year', 'Month', 'Day', 'Decimal_Date', 'Mean_Obs', 'Standard_Deviation', 'Observations',
                           'Definitive/provisional_indicator']
    else:
        sunspot = pd.read_csv('SN_m_tot_V2.0.csv', header=0, delimiter=';')
        sunspot.columns = ['Year', 'Month', 'Decimal_Date', 'Mean_Obs', 'Standard_Deviation', 'Observations',
                           'Definitive/provisional_indicator']
    return sunspot


def clean_sunspot_data(sunspot, year_range, month_range, day_range, obs_periods=None):
    """ Cleans the sunspot dataframe to only have rows associated with the time window specified by the user

        Args:
            sunspot (pd.DataFrame): a dataframe that organizes sunspot data from 1749 to 2022
            year_range (list): year_range[0] contains the min year a row in the dataframe can be associated with, while
                               year_range[1] specifies the max
            month_range (list): month_range[0] contains the min month a row in the dataframe can be associated with,
                                while month_range[1] specifies the max
            day_range (list): day_range[0] contains the min date in a month a row in the dataframe can be associated
                              with, while day_range[1] specifies the max
            obs_periods (str): user-defined number of observation periods (months or days)

        Returns:
            sunspot (pd.DataFrame): an updated version of the sunspot dataframe, which now only includes data in the
                                    range of years specified by the user
    """
    sunspot = sunspot[sunspot.Year >= year_range[0]]
    sunspot = sunspot[sunspot.Year <= year_range[1]]

    sunspot = sunspot[sunspot.Month >= month_range[0]]
    sunspot = sunspot[sunspot.Month <= month_range[1]]

    if obs_periods == 'Days':
        sunspot = sunspot[sunspot.Day >= day_range[0]]
        sunspot = sunspot[sunspot.Day <= day_range[1]]

    return sunspot

# misc.py is part of the 'gus_analysis_code' package.
# It was written by Gus Dunn and was created on 8/10/15.
#
# Please see the license info in the root folder of this package.

"""
Purpose: Contains misc helper-type functions.

=================================================
misc.py
=================================================
"""
__author__ = 'Gus Dunn'

from collections import defaultdict

import pandas as pd


def nested_defaultdict():
    """Simple autovivification-like tree of `defaultdict`s

    Returns:
        defaultdict
    """
    return defaultdict(nested_defaultdict)


def gather(df, key, value, cols):
    """Emulates `tidyr` `gather` to "melt" dataframe by keys and values.

    See "http://connor-johnson.com/2014/08/28/tidyr-and-pandas-gather-and-melt/"

    Args:
        df (pandas.DataFrame): original "un-melted" dataframe.
        key (str): name to use as column title for the new `key` column.
        value (str): name to use as column title for the new `value` column.
        cols (list): list of `str` representations of original column titles to melt into `key`/`value` columns.

    Returns:
        melted_datafrane (pandas.DataFrame): A new dataframe formed by melting `df` by provided info.

    """
    id_vars = [col for col in df.columns if col not in cols]
    id_values = cols
    var_name = key
    value_name = value
    return pd.melt(df, id_vars, id_values, var_name, value_name)

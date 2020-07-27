#! /usr/bin/python
# coding: utf-8
#
# This file is part of PyRemo. PyRemo is a toolbox to facilitate
# treatment and plotting of REMO or other rotated and non-rotated
# data.
#
# Copyright (C) 2010-2014 REMO Group
# See COPYING file for copying and redistribution conditions.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


"""This module is for defining the Remo Code Table

The table in this module contain some meta information about REMO codes
and variable names. The tables define variable names
and codes for the REMO2015 version. The mostly contains:

.. data:: table

**code:**
    integer code.
**name:**
    variable name (REMO standard)
**cf_name:**
    variable name fullfilling Climate and Forecast convention (if available)
**long_name:**
    description (REMO standard)
**unit:**
    unit (REMO standard)
**time_cell_method:**
    time cell method for standard Remo output (mean or inst)


Example:
    Work with the code table and retrieve some information ,e.g.,::

        from pyremo2.codes import table, get_dict

        # print the whole table
        print(table)
        # get dicitonary of a single variable
        t = get_dict('T')
        print(t)
        # or use the code...
        t = get_dict(130)


"""

from ._tables import tables#code_table, read_table

import pandas as pd

table = pd.concat([table for name,table in tables['code'].items()])


def get_dict(id):
    """Returns a dictionary with variable info.

    Searches the code table for a certain variable id.

    Args:
        id (int or str): The variable identifier (might be code or
            variable name).

    Returns:
        varinfo (dict): Dictionary with variable information.

    """
    # id is expected to be a variable name
    if isinstance(id,(str)):
        return get_dict_by_name(id)
    # id is expected to be a code number
    elif isinstance(id, int):
        return get_dict_by_code(id)
    else:
        return None

def get_dict_by_name(varname):
    """Returns a dictionary with variable info.

    Searches the code table for a certain variable name.

    Args:
        varname (str): The variable name.

    Returns:
        varinfo (dict): Dictionary with variable information.

    """
    df = table.loc[table['variable']==varname]
    code = df.index[0]
    dict = df.where(pd.notnull(df), None).to_dict(orient='list')
    dict = { key:item[0] for key, item in dict.items() }
    dict['code'] = code
    return dict


def get_dict_by_code(code):
    """Returns a dictionary with variable info.

    Searches the code table for a certain variable code.

    Args:
        code (int): The variable code.

    Returns:
        varinfo (dict): Dictionary with variable information.

    """
    series = table.loc[code]
    dict = series.where(pd.notnull(series), None).to_dict()
    dict['code'] = code
    return dict

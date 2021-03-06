# -*- coding: utf-8 -*-
# flake8: noqa
"""Remo dataset module.

This module contains functions to work with REMO datasets.

"""

# flake8: noqa
from . import codes

try:
    import cdo
except:
    print("no python-cdo binding installed, unable to read IEG")


def open_remo_dataset(
    filename, options="", update_meta=False, returnX=True, inplace=False, **kwargs
):
    """Read a REMO dataset.

    Read in a REMO dataset into xarray.Dataset or netCDF4.Dataset from IEG or NetCDF and
    provide meta data.

    Parameters
    ----------
    filename : str
        Filename of IEG or NetCDF file.
    update_meta: bool
        Update variable meta information of the dataset from REMO tables.
    returnX : bool
        Return an xarray.Dataset. If False, use netCDF4 Dataset.
    inplace: bool
        Update meta info on disk, only useful for netCDF4 Datasets.

    Returns
    -------
    dataset
        Returns an xarray.Dataset or netCDF4.Dataset.

    """
    format = _get_fileformat(filename)
    # print(format)
    if "NetCDF" in format and not options:
        ds = _read_nc_dataset(filename, returnX=returnX, inplace=inplace, **kwargs)
    elif "IEG" in format:
        if returnX:
            ds = _read_with_cdo(filename, options, returnXDataset=True)
        else:
            ds = _read_with_cdo(filename, options, returnCdf=not inplace)
            if inplace:
                ds = _read_nc_dataset(ds, returnX=False, inplace=inplace)
    else:
        ds = _read_nc_dataset(filename, returnX, **kwargs)
    if update_meta:
        return update_meta_info(ds)
    return ds


def _read_nc_dataset(filename, returnX=True, inplace=False, **kwargs):
    """Use xarray or netCDF4 to read NetCDF."""
    if returnX:
        import xarray as xr

        return xr.open_dataset(filename, **kwargs)
    else:
        from netCDF4 import Dataset

        if inplace:
            mode = "a"
        else:
            mode = "r"
        return Dataset(filename, mode="a")


def _read_with_cdo(filename, options="", **kwargs):
    """uses cdo to read unknown file format."""
    from cdo import Cdo

    return Cdo().copy(options=options, input=filename, **kwargs)


def _get_fileformat(filename):
    """"""
    try:
        from cdo import Cdo

        return Cdo().showformat(input=filename)[0]
    except:
        return 'Unknown'


def update_meta_info(ds, id=None):
    """Updates meta info of a dataset.

    Updates variable names and attributes in a xarray or netCDF4 dataset
    based on Remo table.

    Parameters
    ----------
    ds : dataset
        The dataset in which meta info should be updated.

    Returns
    -------
    dataset
        The dataset with updated meta information.

    """
    meta = {var: _get_meta_info(ds[var]) for var in ds.variables}
    renames = {var: info["variable"] for var, info in meta.items() if info if not None}
    ds = _update_attrs(ds, meta)
    ds = _rename_ds(ds, renames)
    return ds


def _get_meta_info(da, id=None):
    """Get meta info for a netcdf variable."""
    if id:
        attrs = codes.get_dict(id)
    else:
        try:
            attrs = codes.get_dict(da.name)
        except:
            try:
                attrs = codes.get_dict(da.code)
            except:
                attrs = None
    return attrs


def _rename_ds(ds, renames):
    """Rename variables in a dataset."""
    try:  # xarray
        return ds.rename(renames)
    except:  # netCDF4
        for old, new in renames.items():
            if old != new:
                ds.renameVariable(old, new)
        return ds


def _update_attrs(ds, meta):
    """Update variable attributes in a dataset."""
    for var, info in meta.items():
        if info:
            filter_info = {key: value for key, value in info.items() if value}
            # print(filter_info)
            try:  # xarray
                ds[var].attrs.update(filter_info)
            except:  # netCDF4
                ds[var].setncatts(filter_info)
    return ds

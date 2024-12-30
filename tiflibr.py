from datetime			import datetime, timedelta
from matplotlib.colors	import TwoSlopeNorm, CenteredNorm
from rasterio.warp		import reproject, calculate_default_transform
from rasterio.enums 	import Resampling
from rasterio.io		import MemoryFile
from rasterio.plot		import show
from rasterio.mask		import mask

import matplotlib.pyplot	as plt
import geopandas			as gpd
import rasterio				as rs
import numpy				as np
import glob					as g
import inquirer
import re
import io

def get_date(filename):
	match = re.search(r'doy(\d{4})(\d{3})', filename)
	if match:
		year = int(match.group(1))
		day_of_year = int(match.group(2))
		date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
	return date.strftime('%Y-%m-%d')


def get_name(product, file):
	name  = []
	parts = file.split('_')

	name.append(get_date(file))
	if product == "modis":
		name.append(parts[0])
		name.append(parts[1] + " " + parts[2])
	else:
		name.append(parts[0])
		name.append(parts[4])

	return name[0] + " " + name[1] + " " + name[2]

def get_bounds(data):
	w, s, e, n = data.bounds
	return [w, e, s, n]

def get_part(data, area):
	out, tform = mask(data, [area.boundary[0], area.geometry[0]], crop=True)
	out = np.where(out<=0, np.nan, out)

	meta = data.meta.copy()
	meta.update({
		"driver": "GTiff",
		"height": out.shape[1],
		"width": out.shape[2],
		"transform": tform
	})

	file = MemoryFile().open(**meta)
	file.write(out)
	return file

def get_cutoff(data):
	arr = data.flatten()
	nanarr = np.where(arr>=np.mean(arr), np.nan, arr)
	return np.nanmax(nanarr)

def get_param(data, area):
	newdata = get_part(data, area)
	values  = newdata.read(1)
	extent  = get_bounds(newdata)
	cut     = get_cutoff(values)
	image   = np.where(values>cut, np.nan, values)
	image   = np.where(image<=0, np.nan, image)

	return image, extent

def get_newres(data70, data500):
	new_tra = data500.transform
	new_wid = data500.width
	new_hei = data500.height
	new_crs = data500.crs

	data70_res = np.empty((
			data70.count,
			new_hei,
			new_wid
		),
		dtype=data70.dtypes[0]
	)

	reproject(
		source=rs.band(data70, 1),
		destination=data70_res,
		src_transform=data70.transform,
		src_crs=data70.crs,
		dst_transform=new_tra,
		dst_crs=new_crs,
		resampling=Resampling.bilinear
	)

	data70_res = np.where(data70_res<=0, np.nan, data70_res)

	meta = data500.meta.copy()
	meta.update({
		"driver": "GTiff",
		"height": new_hei,
		"width": new_wid,
		"transform": new_tra
	})

	file = MemoryFile().open(**meta)
	file.write(data70_res)
	return file

def get_comb(aqua, terra):
	aqu_data = aqua.read(1)
	ter_data = terra.read(1)

	avg_data = (aqu_data + ter_data) / 2
	meta = aqua.meta.copy()
	meta.update({
		"driver": "GTiff",
		"height": avg_data.shape[0],
		"width": avg_data.shape[1],
	})

	file = MemoryFile().open(**meta)
	file.write(avg_data, 1)
	return file

def get_vmin(*args):
	vmin = np.nanmin(args[0])
	if len(args) != 1:
		for arr in args:
			if np.nanmin(arr) < vmin:
				vmin = np.nanmin(arr)

	return vmin

def get_vmax(*args):
	vmax = np.nanmax(args[0])
	if len(args) != 1:
		for arr in args:
			if np.nanmax(arr) > vmax:
				vmax = np.nanmax(arr)

	return vmax

def get_rmse(meas_1, meas_2):
	return np.sqrt(np.nanmean((meas_2 - meas_1)**2))

def get_mae(meas_1, meas_2):
	return np.nanmean(np.abs(meas_2 - meas_1))

def get_mbe(meas_1, meas_2):
	return np.nanmean(meas_2 - meas_1)

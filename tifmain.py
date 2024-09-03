#!/usr/bin/env python

# ECOSTRESS https://lpdaac.usgs.gov/products/eco3etptjplv001/
# MODIS     https://lpdaac.usgs.gov/products/mod16a2v061/

from tiflibr import *
from tiffunc import *

def main():
	datapath = "data/POL2/"
	areapath = "data/geojson/"

	area = gpd.read_file(areapath + "opn.geojson"), "OPN"

	MOD = rs.open(datapath + "MOD16A2GF.061_LE_500m_doy2020225_aid0001.tif")
	MYD = rs.open(datapath + "MYD16A2GF.061_LE_500m_doy2020225_aid0001.tif")
	ECO = rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020227094517_aid0001.tif")

	ECOd = (rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020211155939_aid0001.tif"),
			rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020219125235_aid0001.tif"),
			rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020220151849_aid0001.tif"),
			rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020227094517_aid0001.tif"),
			rs.open(datapath + "ECO3ETPTJPL.001_EVAPOTRANSPIRATION_PT_JPL_ETdaily_doy2020235063827_aid0001.tif"))

	#for data in ECOd:
	#	draw(data, area, "ECOSTRESS 70 m:")

	#aquaterra_comp(MYD, MOD, area)

	#ecomod_comp(ECO, MOD, area, False)
	ecomod_comp(ECO, MYD, area, False)

	#ecomod_comp(ECO, MOD, area, True)

if __name__ == "__main__":
	main()

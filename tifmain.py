#!/usr/bin/env python

# ECOSTRESS https://lpdaac.usgs.gov/products/eco3etptjplv001/
# MODIS     https://lpdaac.usgs.gov/products/mod16a2v061/

from tiflibr import *
from tiffunc import *

def main():
	datapath = "data/POL/"
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

	#i = 1
	#for data in ECOd:
	#	draw(data, area, i, "ECOSTRESS 70 m:", "eco-date", False)
	#	i+=1

	#aquaterra_comp(MYD, MOD, area, False, "aquter", False)

	#ecomod_comp(ECO, MOD, area, False, "ecomod", False)
	#diff_comp(ECO, MOD, area, "ECOSTRESS / MODIS", "ecomod_4", False, True)

	#ecomod_comp(ECO, MYD, area, False, "ecomyd", False)
	#diff_comp(ECO, MYD, area, "ECOSTRESS / MODIS", "ecomyd_4", False, True)

	CMB = get_comb(MOD, MYD)
	ecomod_comp(ECO, CMB, area, False, "ecocmb", False, MOD.name)
	diff_comp(ECO, CMB, area, "ECOSTRESS / MODIS", "ecocmb_4", False, True)

if __name__ == "__main__":
	main()

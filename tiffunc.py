from tiflibr import *

def chfile(path, product):
	match product.lower():
		case "modis":
			sig = "MOD"
		case "ecostress":
			sig = "ECO"
		case _:
			print("Invalid product name")
			return None

	dictionary = {}
	filenames  = []
	for file in g.glob(path + "*" + sig + "*.tif"):
		name = get_name(product, file.replace(path, ""))
		filenames.append(name)
		dictionary[name] = file

	questions = [inquirer.List('file', message="Choose a file", choices=sorted(filenames))]
	answers   = inquirer.prompt(questions)

	return rs.open(dictionary[answers['file']])

def charea(path):
	files = []
	for file in g.glob(path + "*.geojson"):
		files.append(file)

	questions = [inquirer.List('file', message="Choose an area", choices=files)]
	answers   = inquirer.prompt(questions)

	return gpd.read_file(answers['file']), answers['file']

def histogram(data, bins=2000):
	plt.hist(data.read(1).flatten(), bins=bins)
	plt.show()

def draw(data, geojson, it, product="product", name="image", saveToFile=False):
	area, aname = geojson

	fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(3, 6), gridspec_kw={'height_ratios': [2, 1]})
	ax1.set_title(product + " " + get_date(data.name))
	ax2.set_title("Spektrum Wartości")

	image, extent = get_param(data, area)
	vmin, vmax = np.nanmin(image), np.nanmax(image)

	img = ax1.imshow(image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=extent)
	ax2.hist(image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax2.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax2.set_ylabel("Zliczenia")
	ax2.axvline(np.nanmean(image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(image):.2f} W/m\u00b2")

	area.boundary.plot(color="royalblue", label=aname, ax=ax1)

	ax1.legend()
	ax2.legend()

	fig.colorbar(img, ax=ax1, shrink=0.8).set_label("ET [W/m\u00b2]")

	plt.tight_layout()
	fig.subplots_adjust(left=0.14, right=0.96)

	if saveToFile:
		fig.savefig("pix/"+name+"_"+str(it)+".pdf", format='pdf', bbox_inches='tight')
	else:
		plt.show()

def ecomod_comp(ecost, modis, geojson, normalise=False, name="Image", saveToFile=False, date="NONE"):
	if date == "NONE":
		date = get_date(modis.name)
	else:
		date = get_date(date)

	area, aname = geojson

	ndata = get_newres(ecost, modis)

	fig1, (ax12, ax11) = plt.subplots(1, 2, figsize=(6, 3))
	fig2, (ax22, ax21) = plt.subplots(1, 2, figsize=(6, 3))
	fig3, (ax32, ax31) = plt.subplots(1, 2, figsize=(6, 3))

	ax11.set_title("MODIS 500 m: " + date + "\n")
	ax11.text(0.5, 1.02, "(oryginał)", fontsize=10, ha='center', transform=ax11.transAxes)
	ax12.set_title("Spektrum Wartości")

	ax21.set_title("ECOSTRESS 70 m: " + get_date(ecost.name) + "\n")
	ax21.text(0.5, 1.02, "(oryginał)", fontsize=10, ha='center', transform=ax21.transAxes)
	ax22.set_title("Spektrum Wartości")

	ax31.set_title("ECOSTRESS 500 m:" + get_date(ecost.name) + "\n")
	ax31.text(0.5, 1.02, "(przeskalowany)", fontsize=10, ha='center', transform=ax31.transAxes)
	ax32.set_title("Spektrum Wartości")

	mod_image, mod_extent = get_param(modis, area)
	mod_image = mod_image / 8
	eco_image, eco_extent = get_param(ecost, area)
	res_image, res_extent = get_param(ndata, area)

	if normalise:
		mod_image = mod_image / np.nanmax(mod_image) * 100
		eco_image = eco_image / np.nanmax(eco_image) * 100
		res_image = res_image / np.nanmax(res_image) * 100

	print(f"ECOSTRESS original stdev = {np.nanstd(eco_image)}")
	print(f"ECOSTRESS rescaled stdev = {np.nanstd(res_image)}")
	print(f"MODIS stdev = {np.nanstd(mod_image)}")
	print(f"RMSE = {get_rmse(mod_image, res_image)}")
	print(f"MAE  = {get_mae(mod_image, res_image)}")
	print(f"MBE  = {get_mbe(mod_image, res_image)}")

	vmin = get_vmin(mod_image, eco_image, res_image)
	vmax = get_vmax(mod_image, eco_image, res_image)

	im11 = ax11.imshow(mod_image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=mod_extent)
	ax12.hist(mod_image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax12.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax12.set_ylabel("Zliczenia")
	ax12.axvline(np.nanmean(mod_image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(mod_image):.2f} W/m\u00b2")

	im21 = ax21.imshow(eco_image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=eco_extent)
	ax22.hist(eco_image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax22.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax22.set_ylabel("Zliczenia")
	ax22.axvline(np.nanmean(eco_image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(eco_image):.2f} W/m\u00b2")

	im31 = ax31.imshow(res_image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=res_extent)
	ax32.hist(res_image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax32.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax32.set_ylabel("Zliczenia")
	ax32.axvline(np.nanmean(res_image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(res_image):.2f} W/m\u00b2")

	hist_ymax = max(ax12.get_ylim()[1], ax32.get_ylim()[1])
	ax12.set_ylim(0, hist_ymax)
	ax32.set_ylim(0, hist_ymax)

	area.boundary.plot(color="royalblue", label=aname, ax=ax11)
	area.boundary.plot(color="royalblue", label=aname, ax=ax21)
	area.boundary.plot(color="royalblue", label=aname, ax=ax31)

	ax11.legend()
	ax21.legend()
	ax31.legend()
	ax12.legend()
	ax22.legend()
	ax32.legend()

	fig1.colorbar(im11, ax=ax11).set_label("ET [W/m\u00b2]")
	fig2.colorbar(im21, ax=ax21).set_label("ET [W/m\u00b2]")
	fig3.colorbar(im31, ax=ax31).set_label("ET [W/m\u00b2]")

	plt.tight_layout()
	fig1.subplots_adjust(left=0.1, right=0.96, bottom=0.12, top=0.87)
	fig2.subplots_adjust(left=0.1, right=0.96, bottom=0.12, top=0.87)
	fig3.subplots_adjust(left=0.1, right=0.96, bottom=0.12, top=0.87)

	if saveToFile:
		fig1.savefig("pix/"+name+"_1.pdf", format='pdf', bbox_inches='tight')
		fig2.savefig("pix/"+name+"_2.pdf", format='pdf', bbox_inches='tight')
		fig3.savefig("pix/"+name+"_3.pdf", format='pdf', bbox_inches='tight')
	else:
		plt.show()

def aquaterra_comp(aqua, terra, geojson, normalise=False, name="Image", saveToFile=False):
	area, aname = geojson

	fig1, (ax11, ax12) = plt.subplots(2, 1, figsize=(3, 6), gridspec_kw={'height_ratios': [2, 1]})
	fig2, (ax21, ax22) = plt.subplots(2, 1, figsize=(3, 6), gridspec_kw={'height_ratios': [2, 1]})
	fig3, (ax31, ax32) = plt.subplots(2, 1, figsize=(3, 6), gridspec_kw={'height_ratios': [2, 1]})

	ax11.set_title("TERRA 500 m (oryginał): " + get_date(terra.name))
	ax12.set_title("Spektrum Wartości")

	ax21.set_title("AQUA 500 m (oryginał): " + get_date(aqua.name))
	ax22.set_title("Spektrum Wartości")

	ax31.set_title("Porównanie: " + get_date(aqua.name))
	ax32.set_title("Spektrum Różnic")

	ter_image, ter_extent = get_param(terra, area)
	ter_image = ter_image / 8
	aqu_image, aqu_extent = get_param(aqua, area)
	aqu_image = aqu_image / 8

	if normalise:
		ter_image = ter_image / np.nanmax(ter_image) * 100
		aqu_image = aqu_image / np.nanmax(aqu_image) * 100

	rat_image = np.abs(ter_image - aqu_image)

	print(f"TERRA stdev = {np.nanstd(ter_image)}")
	print(f"AQUA stdev = {np.nanstd(aqu_image)}")
	print(f"DIFF stdev = {np.nanstd(rat_image)}")
	print(f"RMSE = {get_rmse(ter_image, aqu_image)}")
	print(f"MAE  = {get_mae(ter_image, aqu_image)}")
	print(f"MBE  = {get_mbe(ter_image, aqu_image)}")

	vmin = get_vmin(ter_image, aqu_image)
	vmax = get_vmax(ter_image, aqu_image)

	im11 = ax11.imshow(ter_image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=ter_extent)
	ax12.hist(ter_image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax12.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax12.set_ylabel("Zliczenia")
	ax12.axvline(np.nanmean(ter_image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(ter_image):.2f} W/m\u00b2")

	im21 = ax21.imshow(aqu_image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=aqu_extent)
	ax22.hist(aqu_image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax22.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax22.set_ylabel("Zliczenia")
	ax22.axvline(np.nanmean(aqu_image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. ET = {np.nanmean(aqu_image):.2f} W/m\u00b2")

	hist_ymax = max(ax12.get_ylim()[1], ax22.get_ylim()[1])
	ax12.set_ylim(0, hist_ymax)
	ax22.set_ylim(0, hist_ymax)

	im31 = ax31.imshow(rat_image, cmap="magma", extent=aqu_extent)
	ax32.hist(rat_image.flatten(), bins=np.linspace(np.nanmin(rat_image), np.nanmax(rat_image), 20), color="indigo")
	ax32.set_xlabel("Ewapotranspiracja [W/m\u00b2]")
	ax32.set_ylabel("Zliczenia")
	ax32.axvline(np.nanmean(rat_image), color="red", linestyle="--", linewidth=2, label=f"Śr. ΔET = {np.nanmean(rat_image):.2f} W/m\u00b2")

	area.boundary.plot(color="royalblue", label=aname, ax=ax11)
	area.boundary.plot(color="royalblue", label=aname, ax=ax21)
	area.boundary.plot(color="red", label=aname, ax=ax31)

	ax11.legend()
	ax21.legend()
	ax31.legend()
	ax12.legend()
	ax22.legend()
	ax32.legend()

	fig1.colorbar(im11, ax=ax11).set_label("ET [W/m\u00b2]")
	fig2.colorbar(im21, ax=ax21).set_label("ET [W/m\u00b2]")
	fig3.colorbar(im31, ax=ax31).set_label("ΔET [W/m\u00b2]")

	plt.tight_layout()
	fig1.subplots_adjust(left=0.14, right=0.96)
	fig2.subplots_adjust(left=0.14, right=0.96)
	fig3.subplots_adjust(left=0.14, right=0.96)

	if saveToFile:
		fig1.savefig("pix/"+name+"_1.pdf", format='pdf', bbox_inches='tight')
		fig2.savefig("pix/"+name+"_2.pdf", format='pdf', bbox_inches='tight')
		fig3.savefig("pix/"+name+"_3.pdf", format='pdf', bbox_inches='tight')
	else:
		plt.show()

def diff_comp(data2, data1, geojson, title="Image", name="Image", normalise=False, saveToFile=False):
	area, aname = geojson
	data3 = get_newres(data2, data1)

	data1_image, data1_extent = get_param(data1, area)
	data1_image = data1_image / 8
	data3_image, data3_extent = get_param(data3, area)

	if normalise:
		data1_image = data1_image / np.nanmax(data1_image) * 100
		data3_image = data3_image / np.nanmax(data3_image) * 100

	image  = (data3_image - data1_image) / data1_image
	extent = data1_extent

	vmin = get_vmin(image)
	vmax = get_vmax(image)

	fig, (ax2, ax1) = plt.subplots(1, 2, figsize=(6, 3))
	ax1.set_title(title)
	ax2.set_title("Spektrum Wartości")

	img = ax1.imshow(image, cmap="YlOrBr_r", vmin=vmin, vmax=vmax, extent=extent)
	ax2.hist(image.flatten(), bins=np.linspace(vmin, vmax, 20), color="#ff7f0e")
	ax2.set_xlabel("Różnica względna")
	ax2.set_ylabel("Zliczenia")
	ax2.axvline(np.nanmean(image), color="royalblue", linestyle="--", linewidth=2, label=f"Śr. RW = {np.nanmean(image):.2f}")

	area.boundary.plot(color="royalblue", label=aname, ax=ax1)

	ax1.legend()
	ax2.legend()

	fig.colorbar(img, ax=ax1).set_label("Różnica względna")

	plt.tight_layout()
	fig.subplots_adjust(left=0.14, right=0.96)

	if saveToFile:
		fig.savefig("pix/"+name+".pdf", format='pdf', bbox_inches='tight')
	else:
		plt.show()

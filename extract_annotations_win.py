import xml.etree.ElementTree as ET
import sys
from PIL import Image, ImageOps
import glob

# script for cropping out bounding boxes created with labelImg
# use: python extract_annotations.py inputdir outputdir
# first command line parameter is path to directory with annotation files (XML)
# second command line parameter is path to output directory

def retrieve_boxes(infilename, outpath):
	tree = ET.parse(infilename)
	root = tree.getroot()
	for child in root:
		if child.tag == 'path':
			imgfullpath = child.text
		if child.tag == 'filename':
			imgfilename = child.text
	img = Image.open(imgfullpath)
	img = ImageOps.exif_transpose(img)
	boxcount = 0
	for child in root:
		if child.tag == 'object':
			for item in child:
				if item.tag == 'name':
					objectname = item.text
			for item in child:
				if item.tag == 'bndbox':
					xmin = int(item[0].text)
					ymin = int(item[1].text)
					xmax = int(item[2].text)
					ymax = int(item[3].text)
					print(xmin, ymin, xmax, ymax)
					boxcontent = img.crop((xmin, ymin, xmax, ymax))
					outname = outpath + imgfilename.split('.')[0] + '_' + objectname + str(boxcount) + '.' + imgfilename.split('.')[1]
					boxcontent.save(outname)
					boxcount = boxcount + 1
	img.close()

infoldername = sys.argv[1]
if (infoldername[len(infoldername)-1] != '\\'):
	infoldername = infoldername + '\\'
print("input path: "+infoldername)
outpath = sys.argv[2]
if (outpath[len(outpath)-1] != '\\'):
	outpath = outpath + '\\'
print("output path: "+outpath)

imagenamelist = glob.glob(infoldername+'*.xml')

for infilename in imagenamelist:
	retrieve_boxes(infilename, outpath)

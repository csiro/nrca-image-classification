# converts all image files in a folder to JPG format

import sys
from PIL import Image
import glob

#get first command line parameter which is assumed to be folder path

foldername = sys.argv[1]
if (foldername[len(foldername)-1] != '/'):
	foldername = foldername + '/'

#second parameter is input file extension

fileext = sys.argv[2]

#third parameter is output folder

outfoldername = sys.argv[3]
if (outfoldername[len(outfoldername)-1] != '/'):
	outfoldername = outfoldername + '/'

#get names of images

imagenamelist = glob.glob(foldername+'*.'+fileext)

for i in range(0,len(imagenamelist)):
	testimage = Image.open(imagenamelist[i])
	nameonly = imagenamelist[i].split('/')[len(imagenamelist[i].split('/'))-1]
	testimage.convert('RGB').save(outfoldername+nameonly[0:(len(nameonly)-4)]+'.jpg')
	testimage.close()

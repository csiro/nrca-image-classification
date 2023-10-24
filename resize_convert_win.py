# resizes all files in a folder by the value given in the second command line parameter
# if <100, resizing is by percent of original size; if >100, it is the final width in pixels

# use: python resize_convert.py inputfolder edgesize outputfolder inputfileextension
# example: python resize_convert.py /datasets/work/.../ 1024 ./ tif

import sys
from PIL import Image
import glob
import random

#get first command line parameter which is assumed to be folder path

foldername = sys.argv[1]
if (foldername[len(foldername)-1] != '\\'):
	foldername = foldername + '\\'

# fourth parameter is extension

extension = sys.argv[4]
if extension[0] != '.':
	extension = '.'+extension

#third parameter is now output folder

outfoldername = sys.argv[3]
if (outfoldername[len(outfoldername)-1] != '\\'):
	outfoldername = outfoldername + '\\'

#get names of images

imagenamelist = glob.glob(foldername+'*'+extension)

# check second parameter; if <100, assume percent; if >100, assume pixels for width

newsize = int(sys.argv[2])

for i in range(0,len(imagenamelist)):
	testimage = Image.open(imagenamelist[i])
	nameonly = imagenamelist[i].split('\\')[len(imagenamelist[i].split('\\'))-1]
	w, h = testimage.size
	if (newsize<100):
		# assume percentage has been provided in second parameter
		wsize = int(w * float(newsize) / 100)
		hsize = int(h * float(newsize) / 100)
		newimage = testimage.resize((wsize, hsize), Image.ANTIALIAS)
		#newimage.save(imagenamelist[i][0:(len(imagenamelist[i])-4)]+'_'+str(newsize)+'perc'+imagenamelist[i][(len(imagenamelist[i])-4):len(imagenamelist[i])])
	else:
		# assume pixels for shorter edge have been provided in second parameter
		if (w<h):
			wpercent = (newsize / float(w))
			hsize = int((float(h) * float(wpercent)))
			newimage = testimage.resize((newsize, hsize), Image.ANTIALIAS)
			#newimage.save(imagenamelist[i][0:(len(imagenamelist[i])-4)]+'_'+str(newsize)+'pixels'+imagenamelist[i][(len(imagenamelist[i])-4):len(imagenamelist[i])])
		else:
			hpercent = (newsize / float(h))
			wsize = int((float(w) * float(hpercent)))
			newimage = testimage.resize((wsize, newsize), Image.ANTIALIAS)
	newimage.convert('RGB').save(outfoldername+nameonly[0:(len(nameonly)-4)]+'_resized.jpg')
	testimage.close()

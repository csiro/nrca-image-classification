import sys, getopt
import glob
import random
import math
import os

#default parameters
valperc = 15
outputdir = "./"
reduce = False

#parse parameters

try:
	opts, args = getopt.getopt(sys.argv[1:],"hro:v:i:")
except getopt.GetoptError:
	print('Use: prepare_training_library.py -i <inputdirectory> -o <outputdirectory> -v <validationset> -r')
	print('More details: prepare_training_library.py -h')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print('\nUse: prepare_training_library.py -i <inputdirectory> -o <outputdirectory> -v <validationset> -r')
		print('\nParameters')
		print('i: Path to directory containing input image library organised into folders by class name. The folder should not contain any other files apart from those folders.')
		print('o: Path to output directory, default is current working directory.')
		print('r: Add this option if images have been rotated; only first of every four images will be copied.')
		print('v: Percentage of images to be set aside for validation set.\n')
		sys.exit()
	elif opt == "-i":
		inputdir = arg
		if inputdir[len(inputdir)-1] != "/":
			inputdir = inputdir + "/"
	elif opt in ("-o"):
		outputdir = arg
		if outputdir[len(outputdir)-1] != "/":
			outputdir = outputdir + "/"
	elif opt in ("-v"):
		valperc = int(arg)
	elif opt in ("-r"):
		reduce = True

datadir = outputdir + 'data/'
if not os.path.exists(datadir):
	os.makedirs(datadir)
traindir = datadir + 'train/'
if not os.path.exists(traindir):
	os.makedirs(traindir)
valdir = datadir + 'val/'
if not os.path.exists(valdir):
	os.makedirs(valdir)
testdir = outputdir + 'test_images'
if not os.path.exists(testdir):
	os.makedirs(testdir)

classdirs = glob.glob(inputdir+"*")

for x in range(0,len(classdirs)):
	classname = os.path.basename(classdirs[x])
	while ' ' in classname:
		classname = classname.replace(' ', '_')
	thistraindir = traindir + classname + '/'
	if not os.path.exists(thistraindir):
		os.makedirs(thistraindir)
	thisvaldir = valdir + classname + '/'
	if not os.path.exists(thisvaldir):
		os.makedirs(thisvaldir)
	imgfiles = glob.glob(classdirs[x]+'/*')
	# reduce image to one quarter if -r is set
	if reduce:
		imgfiles2 = []
		for y in range(0,len(imgfiles)):
			if (y % 4) == 0:
				imgfiles2.append(imgfiles[y])
		imgfiles = imgfiles2
	# calculate how many images to put aside for val
	valnumber = int(math.ceil(len(imgfiles) * valperc / 100))
	# pick which ones to set aside
	valset = random.sample(imgfiles,valnumber)
	# copy images over
	for y in range(0,len(imgfiles)):
		if imgfiles[y] in valset:
			os.system('cp "'+imgfiles[y]+'" "'+thisvaldir+'"')
		else:
			os.system('cp "'+imgfiles[y]+'" "'+thistraindir+'"')

from PIL import Image
import pytesseract
import sys, getopt
import string
import glob
import os

# default parameters

imgextension = '.jpg'
outputfiledir = './'
inpath = './'
myinstructionsfile = './instructions.txt'
traitlistfile = './character_list.txt'

#parse parameters

try:
	opts, args = getopt.getopt(sys.argv[1:],"hi:o:e:p:t:")
except getopt.GetoptError:
	print('ocr_folder.py -i <inputdir/> -o <outputdir/> -e <inputfileextension>')
	print('More details: ocr_folder.py -h')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print('Script for processing a folder of images for Optical Character Recognition (OCR) with Tesseract. It is assumed that Tesseract is installed and in the command path (for Ubuntu, sudo apt-get install tesseract-ocr.')
		print('\nUse: ocr_folder.py -i <inputdir/> -o <outputdir/> -e <inputfileextension>')
		print('\nParameters')
		print('e: Extension of input image files to be read, default is .jpg')
		print('h: Help, i.e. get this information')
		print('i: Path to directory containing input image files, default is current working directory')
		print('o: Path to directory for output text files, default is current working directory')
		sys.exit()
	elif opt in ("-i"):
		inpath = arg
		if inpath[len(inpath)-1] != "/":
			inpath = inpath + "/"
	elif opt in ("-o"):
		outputfiledir = arg
		if outputfiledir[len(outputfiledir)-1] != "/":
			outputfiledir = outputfiledir + "/"
	elif opt in ("-e"):
		imgextension = arg
		if imgextension[0] != '.':
			imgextension = '.' + imgextension

# glob all the input files assuming they end in fasta
inputfilenames = glob.glob(inpath + "*"+imgextension)


# loop through image files

for x in inputfilenames:
	# OCR using Tesseract
	parsedtext = pytesseract.image_to_string(Image.open(x))
	parsedtext = parsedtext.replace('\n',' ')
	parsedtext = parsedtext.replace('  ',' ')
	parsedtext = parsedtext.replace('—','-')
	imgfilename = os.path.basename(x)
	txtfilename = outputfiledir + imgfilename[0:len(imgfilename)-len(imgextension)] + '.txt'
	with open(txtfilename, 'w') as f:
		f.write(parsedtext)

from PIL import Image
import pytesseract
import sys, getopt
import string
import glob
import os
import time
from openai import AzureOpenAI

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
	print('trait_extract_folder2.py -i <inputdir/> -o <outputdir/> -e <inputfileextension> -p <LLMpromptfile> -t <traitlistfile>')
	print('More details: trait_extract_folder2.py -h')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print('Script for processing a folder of images for Optical Character Recognition (OCR) with Tesseract. It is assumed that Tesseract is installed and in the command path (for Ubuntu, sudo apt-get install tesseract-ocr.')
		print('\nUse: trait_extract_folder2.py -i <inputdir/> -o <outputdir/> -e <inputfileextension> -p <LLMpromptfile> -t <traitlistfile>')
		print('\nParameters')
		print('e: Extension of input image files to be read, default is .jpg')
		print('h: Help, i.e. get this information')
		print('i: Path to directory containing input image files, default is current working directory')
		print('o: Path to directory for output text files, default is current working directory')
		print('p: Text file containing the prompt for the LLM explaining the traits to be extracted. Default is instructions.txt, assumed to be in the current working folder.')
		print('t: Text file containing the list of traits or characters to be extracted, one per text row. Example for Asteraceae is character_list.txt.')
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
	elif opt in ("-p"):
		myinstructionsfile = arg
	elif opt in ("-t"):
		traitlistfile = arg

# glob all the input files assuming they end in fasta
inputfilenames = glob.glob(inpath + "*"+imgextension)

# read prompt file
file = open(myinstructionsfile, "r")
myinstructions = file.read()
file.close()
#print(myinstructions)

# read trait list file
file = open(traitlistfile, "r")
mytraitlist = file.read()
file.close()

# Initialize Azure OpenAI client with key-based authentication
 
endpoint = os.getenv("ENDPOINT_URL", "")     # !!!!!!!!!!!!!! insert relevant endpoint URL as second parameter
deployment = os.getenv("DEPLOYMENT_NAME", "omni")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "")      # !!!!!!!!!!! insert your or your organisations OpenAI subscription key as second parameter
 
client = AzureOpenAI(
    azure_endpoint = endpoint,
    api_key = subscription_key,
    api_version = "2024-02-15-preview",
)

# loop through image files

datatable = []

for x in inputfilenames:
	datarow = []
	# OCR using Tesseract
	parsedtext = pytesseract.image_to_string(Image.open(x))
	parsedtext = parsedtext.replace('\n',' ')
	parsedtext = parsedtext.replace('  ',' ')
	parsedtext = parsedtext.replace('—','-')
	imgfilename = os.path.basename(x)
	txtfilename = outputfiledir + imgfilename[0:len(imgfilename)-len(imgextension)] + '.txt'
	with open(txtfilename, 'w') as f:
		f.write(parsedtext)
	# extract traits with LLM via API call
	completion = client.chat.completions.create(
		model=deployment,
		messages=[
			{"role": "user", "content": parsedtext + "\n" + myinstructions + "\n" + mytraitlist}
		]
	)
	myresponse = completion.choices[0].message.content
	respfilename = outputfiledir + imgfilename[0:len(imgfilename)-len(imgextension)] + '_extracted.txt'
	with open(respfilename, 'w') as f:
		f.write(myresponse)
	# process image file name, assuming taxon and source can be split by '-'
	imgnameparts = imgfilename[0:len(imgfilename)-len(imgextension)].split('-')
	datarow.append(imgnameparts[0])
	datarow.append(imgnameparts[1])
	# extract information from the table returned by the LLM; discard first two rows of table, as they are header and horizontal line
	resplines = myresponse.split('\n')
	tablerowcount = 0
	for y in resplines:
		if y != '':
			if y[0] == '|':
				if tablerowcount > 1:
					thisrow = y[2:]
					while (thisrow[len(thisrow)-1] == ' ') | (thisrow[len(thisrow)-1] == '|'):
						thisrow = thisrow[0:len(thisrow)-1]
					thisrowsplit = thisrow.split('| ')
					# unfortunately, the output sometimes has line breaks leading to empty second column, so have to skip those
					if len(thisrowsplit) > 1:
						trait = thisrowsplit[1]
						datarow.append(trait)
				tablerowcount = tablerowcount + 1
	datatable.append(datarow)
	time.sleep(5)  # artificial wait time because I had a token rate limit error that suggested to wait for two seconds (?)

#write TSV file
outfilename = outputfiledir + 'data_table.tsv'
outfile = open(outfilename, "w")
for x in datatable:
	for y in x:
		outfile.write(y+"\t")
	outfile.write('\n')
outfile.close()

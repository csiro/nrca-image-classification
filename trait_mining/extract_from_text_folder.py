import sys, getopt
import string
import glob
import os
import time
from openai import AzureOpenAI

# default parameters

fileextension = '.txt'
outputfiledir = './'
inpath = './'
myinstructionsfile = './instructions.txt'
traitlistfile = './character_list.txt'

#parse parameters

try:
	opts, args = getopt.getopt(sys.argv[1:],"hi:o:e:p:t:")
except getopt.GetoptError:
	print('extract_from_text_folder.py -i <inputdir/> -o <outputdir/> -e <inputfileextension> -p <LLMpromptfile> -t <traitlistfile>')
	print('More details: extract_from_text_folder.py -h')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print('Script for processing text files with species descriptions to extract traits.')
		print('\nUse: extract_from_text_folder.py -i <inputdir/> -o <outputdir/> -e <inputfileextension> -p <LLMpromptfile> -t <traitlistfile>')
		print('\nParameters')
		print('e: Extension of input text files to be read, default is .txt')
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
		fileextension = arg
		if fileextension[0] != '.':
			fileextension = '.' + imgextension
	elif opt in ("-p"):
		myinstructionsfile = arg
	elif opt in ("-t"):
		traitlistfile = arg

# glob all the input files assuming they end in fasta
inputfilenames = glob.glob(inpath + "*"+fileextension)

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
	print(x)
	datarow = []
	# read x into parsedtext
	txtfilename = os.path.basename(x)
	#txtfilename = outputfiledir + imgfilename[0:len(imgfilename)-len(imgextension)] + '.txt'
	with open(x, 'r') as f:
		parsedtext = f.read()
	# extract traits with LLM via API call
	completion = client.chat.completions.create(
		model=deployment,
		messages=[
			{"role": "user", "content": parsedtext + "\n" + myinstructions + "\n" + mytraitlist}
		]
	)
	myresponse = completion.choices[0].message.content
	respfilename = outputfiledir + txtfilename[0:len(txtfilename)-len(fileextension)] + '_extracted.txt'
	with open(respfilename, 'w') as f:
		f.write(myresponse)
	# process image file name, assuming taxon and source can be split by '-'
	filenameparts = txtfilename[0:len(txtfilename)-len(fileextension)].split('-')
	datarow.append(filenameparts[0])
	datarow.append(filenameparts[1])
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

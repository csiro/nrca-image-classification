import sys, getopt
import string
import glob
import os

# default parameters

outputfiledir = './'
inpath = './'

#parse parameters

try:
	opts, args = getopt.getopt(sys.argv[1:],"hi:o:e:p:")
except getopt.GetoptError:
	print('process_llm_outputs.py -i <inputdir/> -o <outputdir/>')
	print('More details: process_llm_outputs.py -h')
	sys.exit(2)
for opt, arg in opts:
	if opt == '-h':
		print('This is only the last step of trait_extract_folder.py, separated out in case something went wrong with processing the LLM outputs, so that it can be repeated without repeating the API calls.')
		print('\nUse: process_llm_outputs.py -i <inputdir/> -o <outputdir/>')
		print('\nParameters')
		print('h: Help, i.e. get this information')
		print('i: Path to directory containing the tables of traits returned by the LLM. Files must end with _extracted.txt')
		print('o: Path to directory for output data table, default is current working directory')
		sys.exit()
	elif opt in ("-i"):
		inpath = arg
		if inpath[len(inpath)-1] != "/":
			inpath = inpath + "/"
	elif opt in ("-o"):
		outputfiledir = arg
		if outputfiledir[len(outputfiledir)-1] != "/":
			outputfiledir = outputfiledir + "/"

# glob all the input files
inputfilenames = glob.glob(inpath + "*_extracted.txt")

# loop through files

datatable = []

for x in inputfilenames:
	datarow = []
	file = open(x, "r")
	myresponse = file.read()
	file.close()
	# process image file name, assuming taxon and source can be split by '-'
	extrfilename = os.path.basename(x)
	nameparts = extrfilename[0:len(extrfilename)-len('_extracted.txt')].split('-')
	datarow.append(nameparts[0])
	datarow.append(nameparts[1])
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
	
	# write out each species in case the script falls over, so we can still concatenate the outputs
	outfilename = outputfiledir + extrfilename[0:len(extrfilename)-len('_extracted.txt')] + '_processed.txt'
	outfile = open(outfilename, "w")
	for y in datarow:
		outfile.write(y+"\t")
	outfile.write('\n')
	outfile.close()

#write TSV file
outfilename = outputfiledir + 'data_table_reprocessed.tsv'
outfile = open(outfilename, "w")
for x in datatable:
	for y in x:
		outfile.write(y+"\t")
	outfile.write('\n')
outfile.close()

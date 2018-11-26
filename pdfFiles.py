from config import os

def readPdf(fileName):
	""" takes file(pdf) name and return the text in it"""
	from pdfminer.pdfparser import PDFParser
	from pdfminer.pdfdocument import PDFDocument
	from pdfminer.pdfpage import PDFPage
	# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
	from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
	from pdfminer.pdfdevice import PDFDevice
	# Import this to raise exception whenever text extraction from PDF is not allowed
	from pdfminer.pdfpage import PDFTextExtractionNotAllowed
	from pdfminer.layout import LAParams, LTTextBox, LTTextLine
	from pdfminer.converter import PDFPageAggregator

	my_file = fileName
	password=''

	extracted_text = ""

	# Open and read the pdf file in binary mode
	fp = open(my_file, "rb")

	# Create parser object to parse the pdf content
	parser = PDFParser(fp)

	# Store the parsed content in PDFDocument object
	document = PDFDocument(parser, password)

	# Check if document is extractable, if not abort
	if not document.is_extractable:
		raise PDFTextExtractionNotAllowed

	# Create PDFResourceManager object that stores shared resources such as fonts or images
	rsrcmgr = PDFResourceManager()

	# set parameters for analysis
	laparams = LAParams()

	# Create a PDFDevice object which translates interpreted information into desired format
	# Device needs to be connected to resource manager to store shared resources
	# device = PDFDevice(rsrcmgr)
	# Extract the decive to page aggregator to get LT object elements
	device = PDFPageAggregator(rsrcmgr, laparams=laparams)

	# Create interpreter object to process page content from PDFDocument
	# Interpreter needs to be connected to resource manager for shared resources and device 
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	# Ok now that we have everything to process a pdf document, lets process it page by page
	for page in PDFPage.create_pages(document):
		# As the interpreter processes the page stored in PDFDocument object
		interpreter.process_page(page)
		# The device renders the layout from interpreter
		layout = device.get_result()
		# Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
		for lt_obj in layout:
			if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
				extracted_text += lt_obj.get_text()

	#close the pdf file
	fp.close()

	# print (extracted_text.encode("utf-8"))

	with open('Temp.txt', "wb") as my_log:
		my_log.write(extracted_text.encode("utf-8"))


	with open('Temp.txt' , 'r') as f:
			text = f.read()

	try:
		os.remove('Temp.txt')
	except Exception as e:
		pass

	return text


def readDocx(fileName):
	try:
	    from xml.etree.cElementTree import XML
	except ImportError:
	    from xml.etree.ElementTree import XML
	import zipfile

	WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
	PARA = WORD_NAMESPACE + 'p'
	TEXT = WORD_NAMESPACE + 't'


	def get_docx_text(path):
	    """
	    Take the path of a docx file as argument, return the text in unicode.
	    """
	    document = zipfile.ZipFile(path)
	    xml_content = document.read('word/document.xml')
	    document.close()
	    tree = XML(xml_content)

	    paragraphs = []
	    for paragraph in tree.getiterator(PARA):
	        texts = [node.text
	                 for node in paragraph.getiterator(TEXT)
	                 if node.text]
	        if texts:
	            paragraphs.append(''.join(texts))

	    return '\n\n'.join(paragraphs)


	return get_docx_text(fileName)

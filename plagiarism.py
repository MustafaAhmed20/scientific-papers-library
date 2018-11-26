from config import time, render_template, os, escape, secure_filename

from history import saveHistory

import threading

result = []
file1ResultPositions = {}
file2ResultPositions = {}
colorNumberAvlabel = 7
class myThread (threading.Thread):
	def __init__(self, file1SubTextID, file2SubTextID, file1SubTextPosition, file2SubTextPosition, functionName, arg):
		threading.Thread.__init__(self)
		self.functionName = functionName
		self.arg = arg
		self.file1Position = file1SubTextPosition
		self.file2Position = file2SubTextPosition
		self.file1ID = file1SubTextID
		self.file2ID = file2SubTextID
	def run(self):
		self.result = self.functionName(self.arg)

		if str(self.file1ID) not in file1ResultPositions.keys():
			file1ResultPositions[str(self.file1ID)] = []
		if str(self.file2ID) not in file2ResultPositions.keys():
			file2ResultPositions[str(self.file2ID)] = []

		for i in self.result:
			file1ResultPositions[str(self.file1ID)].append(i[0])
			file2ResultPositions[str(self.file2ID)].append(i[1])
			i[0][0] += self.file1Position
			i[0][1] += self.file1Position
			i[1][0] += self.file2Position
			i[1][1] += self.file2Position
			result.append(i)


def main(file1Words, file1Text, file2Words, file2Text):
	
	# sure this variables are clear
	result.clear()
	file1ResultPositions.clear()
	file2ResultPositions.clear()

	maxLength = 5
	minLength = 5 # the minemom number of words to combare in the text

	#result = plagiarism(file1Words, file2Words, maxLength, minLength)
	
	def threadWork():
		global result
		def threadNumbers(length1, length2):
			""" decide the number of threads """
			safetyCounter = 0
			value = min(length1, length2)
			if value <= 120:
				return 1
			divVar = 10
			while True:
				safetyCounter += 1
				if safetyCounter >= 500:
					return divVar
				x = value // divVar
				if x > 60 and x < 130:
					return divVar
				elif x >= 130:
					divVar += 1
				else:
					divVar -= 1

		def sizeCuts(numberOfCuts, fileLength):
			""" get all positions for cut the text """
			value = fileLength // numberOfCuts
			if fileLength % numberOfCuts == 0:
				return list(range(value,fileLength,value))
			else:
				return list(range(value,fileLength,value))[:-1]

		def cutTheText(cutsPositions, file):
			""" slice the file with the positions that given in 'cutsPositions' list."""
			container = []
			start = 0
			for i in cutsPositions:
				container.append(file[start:i])
				start = i
			else:
				container.append(file[start:])
			return container

		threadNumbers = threadNumbers(len(file1Words), len(file2Words))

		file1CutsPositions = sizeCuts(threadNumbers, len(file1Words))
		file2CutsPositions = sizeCuts(threadNumbers, len(file2Words))

		files1SubTexts = cutTheText(file1CutsPositions, file1Words)
		files2SubTexts = cutTheText(file2CutsPositions, file2Words)


		""" use threads to plagiarism the text .
			every thread take slice of the two files and process it."""
		for loop in range(threadNumbers):
			# create threads
			threads = []
			for i in range(threadNumbers):
				otherThread = (i + loop) % threadNumbers
				pastResult = []
				if str(i) in file1ResultPositions.keys():
					for pos in file1ResultPositions[str(i)]:
						pastResult.append([pos,None])
				if str(otherThread) in file2ResultPositions.keys():
					for pos in file2ResultPositions[str(otherThread)]:
						pastResult.append([None, pos])

				if i == 0:
					file1AddressPosition = 0
				else:
					file1AddressPosition = file1CutsPositions[i-1]
				if otherThread == 0:
					file2AddressPosition = 0
				else:
					file2AddressPosition = file2CutsPositions[otherThread-1]

				thread = myThread(i, otherThread, file1AddressPosition, file2AddressPosition, plagiarism2, (files1SubTexts[i], files2SubTexts[otherThread], maxLength, minLength, pastResult))
				threads.append(thread)
				thread.start()
			else:
				# wait the threads to finish
				for thread in threads:
					thread.join()
		else:
			# delete useless variables
			del threadNumbers, file1CutsPositions, file2CutsPositions, files1SubTexts, files2SubTexts


		result.sort()
		#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
		""" fix some threads problems.
			the nested points problem."""
		# for i, pos1 in enumerate(result):
		# 	for pos2 in result[i+1:]:
		# 		# check if pos2 nested with pos1 .. if so move pos2 out of pos1
		# 		if pos2[0][0] >= pos1[0][0] and pos2[0][0] <= pos1[0][1]:
		# 			pos2[0][0] = pos1[0][1] + 1
		# 		if pos2[1][0] >= pos1[1][0] and pos2[1][0] <= pos1[1][1]:
		# 			pos2[1][0] = pos1[1][1] + 1

		#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

		#######################################
		# merge every two sequenced points 
		while True:
			for index, (pos1, pos2) in enumerate(zip(result[:-1], result[1:])):
				if pos1[0][1] == pos2[0][0] -1 and pos1[1][1] == pos2[1][0] -1:
					newPoint = [[pos1[0][0],pos2[0][1]],[pos1[1][0],pos2[1][1]]]

					result.insert(index, newPoint)
					result.remove(pos1)
					result.remove(pos2)

					break
			else:
				break

		#######################################

		# mend the all text-result
		result = mendProcess(result, file1Words, file2Words, minLength - 1)

	threadWork()

	# delete the useless variabels
	del maxLength, minLength
	
	r = []
	for i in result:
		r.append(i[0])
	return r

def Read(file):
	''' open file and return the file as words and as text.'''
	
	text = file

	text = str(escape(text))
	fileAsText = text
	text = text.lower()
	skips = ['\n', '.', '!', '?', '؟', '"', "'", ',', '“', '”', '•', ':', '(', ')', '-', '<', '>', '%', '$']

	# loop over all skips and remove them from the text
	for skip in skips:
		text = text.replace(skip, ' ')

	return text.split(), fileAsText

"""
def plagiarism(file1, file2, maxLength, minLength):
	''' takes two files words and compare them '''
	
	matches = {'file1':[], 'file2':[]} # store every match pos founded
	result = []

	def nextPos(oldBeg, oldEnd, file):
			''' take old position of cuts and return next availabel cuts depend on 'matches' dect '''
			oldBeg += 1
			oldEnd += 1
			for pos in matches[file]:

				if oldEnd < pos[0]:
					return oldBeg, oldEnd

				if oldBeg > pos[1]:
					continue

				if oldBeg  == pos[0]:
					oldEnd += pos[1] + 1 - oldBeg
					oldBeg = pos[1] + 1

				elif oldEnd >= pos[0] and oldEnd <= pos[1]:
					oldEnd += pos[1] + 1 - oldBeg
					oldBeg = pos[1] + 1
			else:
				return oldBeg, oldEnd

	def searchMatch(file1Begining,file2Begining):
		''' search in match list and return match position that '''
		for i in result[::-1]:
			if i[0][1] == file1Begining -1 and i[1][1] == file2Begining -1:
				return i
		else:
			return False

	maxLength -= 1 # use it as index
	minLength -= 1 # use it as index
	if minLength < 0:
		minLength = 0
	file1Length = len(file1)
	file2Length = len(file2)

	while(maxLength >= minLength):
		''' the loop do the cut size of the file '''	

		file1Begining, file1Ending = nextPos(-1, -1 + maxLength, 'file1')

		
		while file1Ending < file1Length: # cut every possible cuts from file 1
			
			file2Begining, file2Ending = nextPos(-1, -1 + maxLength, 'file2')
			
			# file1 sub-text .........
			text1 = file1[file1Begining : file1Ending + 1]
			# ........................

			while file2Ending < file2Length:# cut every possibel cuts from file 2 and compare the two strings

				# file2 sub-text ..........
				text2 = file2[file2Begining : file2Ending + 1]
				# .........................

				if text1 == text2:

					lastValue = searchMatch(file1Begining,file2Begining)
					if lastValue:
						result.remove(lastValue)
						matches['file1'].remove(lastValue[0])
						matches['file2'].remove(lastValue[1])
						newPosition = ((lastValue[0][0], file1Ending),(lastValue[1][0], file2Ending))
						result.append(newPosition)
						matches['file1'].append(newPosition[0])
						matches['file2'].append(newPosition[1])
						
						matches['file1'].sort()
						matches['file2'].sort()
						break
					else:
						result.append(((file1Begining, file1Ending),(file2Begining, file2Ending)))
						matches['file1'].append((file1Begining, file1Ending))
						matches['file2'].append ((file2Begining, file2Ending))
					
						matches['file1'].sort()
						matches['file2'].sort()
					
					

				file2Begining, file2Ending = nextPos(file2Begining, file2Ending, 'file2')

			file1Begining, file1Ending = nextPos(file1Begining, file1Ending, 'file1')

		maxLength -= 1

	def searchPointInMatch(point, file):
		for position in result[::-1]:
			if point >= position[file][0] and point <= position[file][1]:
				return True
		else:
			return False
	
	resultLength = len(result)
	
	for index in range(resultLength-1, -1, -1):
		position = result[index]

		for i in range(3,0,-1):
			if searchPointInMatch(position[0][1] + i, 0) or searchPointInMatch(position[1][1] + i, 1):
				continue
			text1 = file1[position[0][1] + 1 : position[0][1] + i + 1]
			text2 = file2[position[1][1] + 1 : position[1][1] + i + 1]

			if not text1 or not text2:
				break

			if text1 == text2:
				result[index] = ((position[0][0],position[0][1]+i),(position[1][0],position[1][1]+i))
				break
			
	return result
"""

def plagiarism2(parameters):
	''' takes two files words and compare them '''
	
	file1, file2 =  parameters[0], parameters[1]
	maxLength, minLength, pastResult = parameters[2], parameters[3], parameters[4]
	matches = {'file1':[], 'file2':[]} # store every match pos founded
	result = [] #((file1Begining, file1Ending),(file2Begining, file2Ending))
	for position in pastResult:
		if position[0]:
			matches['file1'].append(position[0])
		if position[1]:
			matches['file2'].append(position[1])
	else:
		matches['file1'].sort()
		matches['file2'].sort()

	def nextPos(oldBeg, oldEnd, file):
			''' take old position of cuts and return next availabel cuts depend on 'matches' dect '''
			oldBeg += 1
			oldEnd += 1
			for pos in matches[file]:

				if oldEnd < pos[0]:
					return oldBeg, oldEnd

				if oldBeg > pos[1]:
					continue

				if oldBeg  >= pos[0]:
					oldEnd += pos[1] + 1 - oldBeg
					oldBeg = pos[1] + 1

				elif oldEnd >= pos[0] and oldEnd <= pos[1]:
					oldEnd += pos[1] + 1 - oldBeg
					oldBeg = pos[1] + 1
			else:
				return oldBeg, oldEnd

	def searchMatch(file1Begining,file2Begining):
		''' search in match list and return match position that '''
		for i in result[::-1]:
			if i[0][1] == file1Begining -1 and i[1][1] == file2Begining -1:
				return i
		else:
			return False

	maxLength -= 1 # use it as index
	minLength -= 1 # use it as index
	if minLength < 0:
		minLength = 0
	file1Length = len(file1)
	file2Length = len(file2)

	while(maxLength >= minLength):
		''' the loop do the cut size of the file '''	

		file1Begining, file1Ending = nextPos(-1, -1 + maxLength, 'file1')

		
		while file1Ending < file1Length:
			# cut every possible cuts from file 1
			
			file2Begining, file2Ending = nextPos(-1, -1 + maxLength, 'file2')
			
			# file1 sub-text .........
			text1 = file1[file1Begining : file1Ending + 1]
			# ........................

			while file2Ending < file2Length: 
				# cut every possibel cuts from file 2 and compare the two strings

				# file2 sub-text ..........
				text2 = file2[file2Begining : file2Ending + 1]
				# .........................

				if text1 == text2:

					lastValue = searchMatch(file1Begining,file2Begining)
					if lastValue:
						result.remove(lastValue)
						matches['file1'].remove(lastValue[0])
						matches['file2'].remove(lastValue[1])
						newPosition = [[lastValue[0][0], file1Ending],[lastValue[1][0], file2Ending]]
						result.append(newPosition)
						matches['file1'].append(newPosition[0])
						matches['file2'].append(newPosition[1])
						
						matches['file1'].sort()
						matches['file2'].sort()
						break
					else:
						result.append([[file1Begining, file1Ending],[file2Begining, file2Ending]])
						matches['file1'].append([file1Begining, file1Ending])
						matches['file2'].append ([file2Begining, file2Ending])
					
						matches['file1'].sort()
						matches['file2'].sort()

				file2Begining, file2Ending = nextPos(file2Begining, file2Ending, 'file2')

			file1Begining, file1Ending = nextPos(file1Begining, file1Ending, 'file1')

		maxLength -= 1

	result = mendProcess(result, file1, file2, minLength)
	return result

def mendProcess(result, file1, file2, wordsNumber):
	""" take every match location in 'result' list and get sure
		 there is no sub-text of length(wordsNumber) matched get ignored. """

	def searchPointInMatch(point, file):
		for position in reversed(result):
			if point >= position[file][0] and point <= position[file][1]:
				return True
		else:
			return False

	for position in reversed(result):
		for i in range(wordsNumber, 0, -1):
			if searchPointInMatch(position[0][1] + i, 0) or searchPointInMatch(position[1][1] + i, 1):
				continue
			text1 = file1[position[0][1] + 1 : position[0][1] + i + 1]
			text2 = file2[position[1][1] + 1 : position[1][1] + i + 1]

			if not text1 or not text2:
				break

			if text1 == text2:
				position[0][1] += i
				position[1][1] += i
				break

	return result

def plagiarismText(doerUserId=None, text=None, collegeId=None, justRate=False):

	if  'getFilesID' and 'getFile' not in globals():
		from files import getFilesID, getFile

	file1Words, file1Text = Read(text)

	currentDir = os.getcwd()
	try:
		os.chdir('filesAsText')
	except FileNotFoundError as e:
		os.makedirs('filesAsText')
		os.chdir('filesAsText')

	targetTextsIDs, targetTextsNames = getFilesID(collegeId)
	finalResult = []
	filesPostitons ={}
	for bookID, fileID in enumerate(targetTextsIDs):
		try:
			with open(fileID, 'r') as f:
				file2Text = f.read()
				file2Words = file2Text.split()
		except FileNotFoundError as e:
			# get the file from database if there is't copy of it
			fileAsBainary, file_ext = getFile(fileID)

			# writ the file into temp file just to get it again as text
			with open('temp', 'wb')as f:
				f.write(fileAsBainary)
			del fileAsBainary, file_ext
			file2Words, file2Text = Read(open('temp','r').read())

			os.remove('temp')

			# store the file again as list of words
			with open(fileID, 'w') as f:
				f.write(' '.join(file2Words))

		result = main(file1Words, file1Text, file2Words, file2Text)
		for pos in result:
			filesPostitons[str(pos[0])+'-'+str(pos[1])] = bookID

		finalResult.extend(result)

	finalResult.sort()

	# delete duplicate points (match same string from differend books)
	duplicate = []
	for index, (i, j) in enumerate(zip(finalResult[:-1], finalResult[1:])):
		if i == j:
			duplicate.append(i)
	list(map(lambda a:finalResult.remove(a) ,duplicate))
	del duplicate
	# delete inner match (match inside another)
	while True:
		for i in finalResult:
			out = False
			for l, j in enumerate(finalResult):
				if i == j:
					continue
				if j[0] >= i[0] and j[1] <= i[1]:
					del finalResult[l]
					out = True
					break
			if out:
				break
		else:
			break
	
	# # delete one of intersected points 
	# while True:
	# 	for index, i in enumerate(finalResult):
	# 		out = False
	# 		for l, j in enumerate(finalResult[index+1:]):

	# 			if i[1] >= j[0] >= i[0] or i[1] >= j[1] >= i[0]:
	# 				one = i[1] - i[0]
	# 				two = j[1] - j[0]
	# 				if one > two:
	# 					del finalResult[l]
	# 				else:
	# 					del finalResult[index]
	# 				out = True
	# 				break
	# 		if out:
	# 			break
	# 	else:
	# 		break

	finalText = colorText(file1Text, file1Words, finalResult, filesPostitons)
	temp = []
	for i in finalResult:
		temp.append('"'+targetTextsNames[filesPostitons[str(i[0])+'-'+str(i[1])]]+'"')
	targetTextsNames = temp
	targetTextsNames.insert(0, '"original"')
	del temp

	# calculate the plagiarism rate
	ratesBooks ={}
	sumCopiedWords = 0
	for match in finalResult:
		wordsNumbers = match[1] - match[0] + 1

		book = filesPostitons[str(match[0])+'-'+str(match[1])]
		if str(book) in ratesBooks.keys() :
			ratesBooks[str(book)] += wordsNumbers
		else:
			ratesBooks[str(book)] = wordsNumbers

		sumCopiedWords += wordsNumbers
	
	rates = [100 - ((sumCopiedWords/len(file1Words))*100)]
	if rates[0] < 0.0:
		rates[0] = 0.0
	rates += [ratesBooks[i]/len(file1Words)*100 for i in ratesBooks]
	rates = list(map(lambda r: '%1.2f'%(r), rates))
	rates = list(map(str, rates))
	fRate = sumCopiedWords/len(file1Words)*100
	if fRate > 100.0:
		fRate = 100.0
	fullRate = '%1.2f'%(fRate)

	os.chdir(currentDir)

	if justRate == True:
		return float(fullRate)

	# save the process in the history
	saveHistory(doerUserId, 3)
	return {'fullRate':fullRate, 'text':finalText, 'names':','.join(targetTextsNames), 'rates': ','.join(rates)}

def colorText(text, textAsWords, positions, positionsFiles):
	''' take text and color it in HTML form '''
	file1Text = text
	file1Words = textAsWords
	
	begin = '''<span class="colorText'''
	begin_end = '''">'''
	end = '''</span>'''

	# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
	# this block find and store the indexes of words by finding the '\n' and ' ' charcters
	wordSplits = ('\n', ' ', '-','.')
	def findWordSplitsPositions(wordSplits, file):
		positions = []
		lastChar = False
		for i, char in enumerate(file):
			if char in wordSplits:
				if lastChar :
					positions.pop()
				positions.append(i)
				lastChar = True
			else:
				lastChar = False

		return positions
	
	wordSplits1Positions = findWordSplitsPositions(wordSplits, file1Text)

	del wordSplits
	# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	# *******************************************
	# this block insert begin and ending spans for HTML coloring for matching sub-strings

	def insertMatches(filePosition, wordSplitsPositions, text, fileWords):
		''' this inner function takes file name and insert mathces begining and the ending
		    in the text. '''
		global colorNumberAvlabel

		# some variables
		counter = 0
		fileWordsLength = len(fileWords)
		endingLength = len(end)

		for position in filePosition:

			# insert the start position .........
			colorCode = str( (positionsFiles[str(position[0])+'-'+str(position[1])] % colorNumberAvlabel) + 1)
			insertion = begin + colorCode + begin_end
			if position[0] == 0:
				text = insertion + text
			else:
				pos = wordSplitsPositions[position[0] - 1]
				text = text[:pos + counter] + insertion + text[pos + counter:]	
			counter += len(insertion)
			# ....................................

			# insert End position ................
			if position[1] >= fileWordsLength - 1:
				text = text + end
			else:
				pos = wordSplitsPositions[position[1]]
				text = text[:pos + counter] + end + text[pos + counter:]	
			counter += endingLength
			# ....................................
		return text

	# insert the begining and the ending of matches indexis for file 1
	file1Text = insertMatches(positions, wordSplits1Positions, file1Text, file1Words)


	# delete the useless variabels
	del wordSplits1Positions
	
	# *******************************************

	# replace all '\n' with '<br>' to render the text in HTML page
	file1Text = file1Text.replace('\n', '<br>')
	return file1Text


if __name__ == '__main__':
	main()

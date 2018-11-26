from config import conn, datetime, secure_filename, os, session
from history import saveHistory
from colleges import changeTubleToListOfDects
from plagiarism import plagiarismText
from pdfFiles import readPdf, readDocx


def addNewFile(doerUserId, name, aothor, date, file, collegeId):
	""" add new file to database."""
	fileName = 'tempFile'
	# get the file extension
	file_ext = file.filename.split('.')[-1]

	# save the file to server
	#file.save(secure_filename(file.filename))
	file.save(fileName)
	filesAsText = readFile(fileName, file_ext)

	# do the plagiarism check before add the file to database 
	rate = plagiarismText(text=filesAsText, collegeId=collegeId, justRate=True)
	if rate > session['college_ plagiarism']:
		return 'the plagiarism percentage is higher than allowed '

	# read file as binary
	file_b = readFile(fileName, file_ext, 'binary')

	# get the current time
	cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	# save file to database
	sql = """INSERT INTO projects(name, aothor, date, addedDate, file, file_ext, college_id)
		   	 VALUES(%s,%s, %s, %s, %s, %s, %s)"""
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute(sql,(name, aothor, date, cur_date, file_b, file_ext, collegeId))
			conn("commit")
			conn('close')
			# save the process in the history
			addFileId = getLastFileID()
			if addFileId and saveHistory(doerUserId, 2, addFileId):
				pass
			else:
				return "can't save add user process in the history"

			# save the file in the server as words splits with ' '
			saveFileInServerWithID(filesAsText, addFileId)

		except Exception as e:
			conn('close')
			return False
		finally:
			os.remove(fileName)

	else:
		return False
	return True

def getAllFiles(collegeId=None):
	""" get all the files from database """

	sql = "SELECT projects.name,aothor,date,colleges.name from projects,colleges where  projects.college_id = colleges.id"

	if collegeId:
		sql += ' and college_id = %s'

	sql += ' order by college_id'

	# get data
	cursor = conn('open')
	if cursor:
		if collegeId:
			cursor.execute(sql,(collegeId))
		else:
			cursor.execute(sql)
		data = cursor.fetchall()
		data = changeTubleToListOfDects(data, 'name aothor date college_name')
		for book in data:
			book["aothor"] = book["aothor"].replace(';','<br>')

		conn('close')
		return data
	else:
		return False

def getLastFileID():
	''' get last file-id in the database and return it '''

	# get data
	cursor = conn('open')
	if cursor:
		cursor.execute("SELECT max(id) from projects ")
		data = cursor.fetchone()
		conn('close')
		return data[0]
	else:
		return False

def saveFileInServerWithID(fileText, idName):
	""" takes file text and the id of the file in the database and save it in 
		the server as words splits with ' ' """

	fileText = fileText.lower()
	skips = ['\n', '.', '!', '?', '؟', '"', "'", ',', '“', '”', '•', ':', '(', ')', '-']

	# loop over all skips and remove them from the text
	for skip in skips:
		fileText = fileText.replace(skip, ' ')

	currentDir =  os.getcwd()
	try:
		os.chdir('filesAsText')
	except FileNotFoundError as e:
		os.makedirs('filesAsText')
		os.chdir('filesAsText')

	with open(str(idName), 'w') as f:
		f.write(fileText)

	os.chdir(currentDir)

	return True

def getFilesID(collegeId=None):
	''' return list of files-ids of specific college '''

	# get data
	if collegeId:
		sql = "SELECT id,name from projects where college_id=%s"
	else:
		sql = "SELECT id,name from projects"
	cursor = conn('open')
	if cursor:
		if collegeId:
			cursor.execute(sql, (collegeId))
		else:
			cursor.execute(sql)
		data = cursor.fetchall()
		IDs = []
		names = []
		for i in data:
			IDs.append(str(i[0]))
			names.append(i[1])
		conn('close')
		return IDs, names
	else:
		return False

def getFile(id):
	''' get file from database and return it as bainare file.'''

	# get data
	cursor = conn('open')
	if cursor:
		cursor.execute("SELECT file, file_ext from projects where id=%s", (id))
		data = cursor.fetchone()
		conn('close')
		return data
	else:
		return False

def readFile(filename, fileExe, mood='text'):
	""" mood:binary , text """
	def read_file(filename, mood):
		''' read file as binary and return it '''
		with open(filename, mood) as f:
			file = f.read()
		return file

	if mood == 'binary':
		return read_file(filename, 'rb')
	
	text = ''
	if fileExe == 'txt':
		text =  read_file(filename, 'r')
	elif fileExe == 'pdf':
		text = readPdf(filename)
	elif fileExe == 'docx':
		text = readDocx(filename)
	
	return text



if __name__ == '__main__':
	pass

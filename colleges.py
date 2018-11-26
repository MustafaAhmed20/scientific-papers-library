from config import conn
def addNewCollege(collegeName, plagiarismRate):

	sql = """INSERT INTO colleges(name,plagiarism)
		   	 VALUES(%s,%s)"""
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute(sql,(collegeName, plagiarismRate))
			conn("commit")
			return True
		except Exception as e:
			conn('close')
			return False
	else:
		return False

def getAllColleges(collegID=None):

	sql = "SELECT * from colleges "
	if collegID:
		sql += 'where id = %s'
	# get data
	cursor = conn('open')
	if cursor:
		if collegID:
			cursor.execute(sql, (collegID))
		else:
			cursor.execute(sql)
		data = cursor.fetchall()
		if not data:
			conn('close')
			return False
		else:
			conn('close')
			data = changeTubleToListOfDects(data, 'id name plagiarism')
		return data
	else:
		return False

def changeTubleToListOfDects(data, columns):
	""" this function take the tuble returned by database and tranform it to list of dicts.
		the keys of the dects is the table columns."""
	result = []
	columns = str(columns).split()
	loop = len(columns)
	for row in data:
		d = {}
		for i in range(loop):
			d[str(columns[i])] = row[i]
		result.append(d)
	return result
from config import conn, datetime
from colleges import changeTubleToListOfDects

def getNotification(collegeID=None):
	""" return all users that Waiting for acceptance for spycific college"""
	sql = """SELECT user.u_name, user.name, user.university_id, colleges.name ,user.email
			from user,colleges where state = 2 and user.college_id=colleges.id """
	if collegeID:
		sql += 'and college_id= %s '
	cursor = conn('open')
	if cursor:
		if collegeID:
			cursor.execute(sql,(collegeID) )
		else:
			cursor.execute(sql)
		data = cursor.fetchall()
		data = changeTubleToListOfDects(data, 'u_name name university_id college_name email')
		if not data :
			conn('close')
			return False
		else:
			conn('close')
			return data
			
	else:
		return False

def saveHistory(userId, operationType, varId=None):

	# get the current time
	cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("INSERT INTO history (user_id, operation_type, var_id, date) VALUES(%s, %s, %s, %s)",
						   (userId,
						   	operationType,
						   	varId,
						   	cur_date ))
			conn("commit")
			conn('close')
			return True
		except Exception as e:
			return False
	else:
		conn('close')
		return False

def getHistory():
	cursor = conn('open')
	if cursor:
		cursor.execute("""SELECT user.u_name, user.university_id,
						  colleges.name, history.operation_type, history.date 
						  from history,user,colleges 
						  where history.user_id = user.id and user.college_id = colleges.id""")
		data = cursor.fetchall()
		data = changeTubleToListOfDects(data, 'u_name university_id college_name operation_type date')
		if not data :
			conn('close')
			return False
		else:
			conn('close')
			return data

	else:
		return False

def report(collegeID=None):
	
	from files import getFilesID
	from users import getAllUsers
	from colleges import getAllColleges
	
	data = {}
	
	# get number of Researchs
	data['Researches'], temp = getFilesID(collegeID)
	data['Researches'] = len(data['Researches'])
	del temp

	# get number of colleges
	data['Colleges'] = len(getAllColleges(collegeID))

	# get all members in the system 
	data['Members'] = len(getAllUsers(collegeID))

	# get numbers of the Plagiarisms
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute('SELECT count(id) from history where operation_type = 3')
			data['Plagiarisms'] = cursor.fetchone()[0]
			conn('close')
		except Exception as e:
			pass
	else:
		conn('close')
		pass

	# success
	return data

if __name__ == '__main__':
	pass

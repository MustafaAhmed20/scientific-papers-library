from config import conn, check_password_hash, generate_password_hash
from history import saveHistory
from colleges import changeTubleToListOfDects
def login(userName, password):
	""" takes the user ('username' or 'email') and 'password' and return True if the user info is correct and
 		False other waise. """
	# log-in the user
	cursor = conn('open')
	if cursor:
		cursor.execute("""SELECT user.id, user.u_name, user.u_pass, user.state, user.u_type,
						 user.university_id, user.college_id, user.email, user.name
						from user, colleges
						where (u_name= %s or email= %s) and state = 0 """,
					   (userName, userName) )
		data = cursor.fetchone()
		if not data:
			conn('close')
			return False

		data = changeTubleToListOfDects([data], 'id u_name u_pass state u_type university_id college_id email name')
		if not check_password_hash(data[0]['u_pass'], password):
			conn('close')
			return False			
		else:
			conn('close')
			return data
			
	else:
		return False

def resetUserPassword(oldPass, newpass, conPass, userId):

	if newpass != conPass:
		return "the password don't mathch!", 404

	# get old pass and check it if correct
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("SELECT * from user where id= %s", (userId))
		except Exception as e:
			return False
		rows = cursor.fetchone()
		if not rows:
			conn('close')
			return False
		elif not check_password_hash(rows[2], oldPass):
			return "wrong Password" ,404
		else:
			conn('close')

	# update the user password
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("UPDATE user SET u_Pass= %s where id= %s ",
						   (generate_password_hash(newpass), userId))
			conn("commit")
			conn('close')
		except Exception as e:
			return False
	else:
		conn('close')

	return True

def checkUsername(userName):
	""" check if the userName exist.
		return True if user exists and False if not."""
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("SELECT id FROM user where u_name= %s ",(userName))
			rows = cursor.fetchone()
			if not rows:
				return False

			conn("commit")
			conn('close')
		except Exception as e:
			raise e
	else:
		conn('close')
		return False
	return True

def updateUserPassword(userName, newPassword):
	""" update the user password """

	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("UPDATE user SET u_Pass= %s where u_name= %s ",
						   (generate_password_hash(newPassword), userName))
			conn("commit")
			conn('close')
		except Exception as e:
			return False
	else:
		conn('close')
		return False

	return True

def addNewUser(doerUserId, name, userName, password, state , userType, universityId, collegeId, email):
	""" add new user to database .
		return true if success and false if failed.
		and error massege in some cases."""
	result = addNewUserToDataBase(name, userName, password, state , userType, universityId, collegeId, email)

	if result == True:
		''' save the process in history '''

		addUserId = getLastUserID()

		if addUserId:
			saveHistory(doerUserId, 1, addUserId)
		else:
			return "can't save add user process in the history"

		return True
	else:
		return result

def getAllUsers(collegeId=None):
	""" get all the users for spcific college from database. """

	sql = "SELECT name,university_id,u_name,state,u_type,college_id from user WHERE state < 2 "

	if collegeId:
		sql += ' and college_id = %s AND u_type > 1'
	else:
		sql += '  AND (u_type = 1 or u_type = 2)'

	# get data
	cursor = conn('open')
	if cursor:
		if collegeId:
			cursor.execute(sql,(collegeId))
		else:
			cursor.execute(sql)
		data = cursor.fetchall()
		data = changeTubleToListOfDects(data, 'name university_id u_name state u_type college_id')
		conn('close')
		return data
	else:
		return False

def rigesterNewUser(name, userName, password, universityId, collegeId, email):
	
	return addNewUserToDataBase(name, userName, password, 2, "student", universityId, collegeId, email)

def addNewUserToDataBase(name, userName, password, state , userType, universityId, collegeId, email):

	# dicaied user type
	if userType == "admin":
		userType = 0
	elif userType == "project manager":
		userType = 1
	elif userType == "teacher":
		userType = 2
	elif userType == "student":
		userType = 3

	# check if the username found befor
	if checkUsername(userName):
		return "username found befor. take another one", 404
	
	# insert new user in the dataBase
	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("""INSERT INTO user (u_name, u_Pass, state, u_type, university_id, college_id, email, name)
							  VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""",
						   (userName,
						   	generate_password_hash(password),
						   	state,
						   	userType,
						   	universityId,
						   	collegeId,
						   	email,
						   	name))
			conn("commit")
			conn('close')
			return True
		except Exception as e:
			return False
	else:
		conn('close')
		return False

def getLastUserID():

	# get data
	cursor = conn('open')
	if cursor:
		cursor.execute("SELECT max(id) from user ")
		data = cursor.fetchone()
		conn('close')
		return data[0]
	else:
		return False

def blockUser(userName, state):
	""" block user and de-block the user
		return True if success , False if faild."""

	if state == 'block':
		state = 1
	elif state == 'de-block':
		state = 0
	else:
		return False

	if not checkUsername(userName):
		return False

	cursor = conn('open')
	if cursor:
		try:
			cursor.execute("UPDATE user SET state= %s where u_name= %s ",
						   (state, userName))
			conn("commit")
			conn('close')
		except Exception as e:
			return False
	else:
		conn('close')
		return False

	return True

def answererRequests(userName, Type='accept'):
	""" Accept or Reject user requests to get accounts."""
	if Type == 'accept':
		# must send Email here to the user
		sql = "UPDATE user SET state= 0 where u_name= %s "
	else:
		# must send Email here to the user befor delete him
		sql = "DELETE from user where u_name= %s"

	cursor = conn('open')
	if cursor:
		try:
			cursor.execute(sql,(userName))
			conn("commit")
			conn('close')
		except Exception as e:
			return False
	else:
		conn('close')
		return False

	return True

def setprojectmanager(username,college):
	""" Accept or Reject user requests to get accounts."""
		# must send Email here to the user
	sqlremove = "UPDATE user SET u_type= 2 where college_id = %s "
	sql = "UPDATE user SET u_type= 1 where u_name= %s "

	cursor = conn('open')
	if cursor:
		try:
			cursor.execute(sqlremove,(college))
			cursor.execute(sql,(username))
			conn("commit")
			conn('close')
		except Exception as e:
			return False
	else:
		conn('close')
		return False

	return True
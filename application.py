from config import render_template, request, redirect, session, app, login_required, url_for,os,make_response
import users
import files
import history
import colleges
from plagiarism import plagiarismText

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@login_required
@app.route("/plagiarism", methods=['POST'])
def plagiarism():
	text=None
	file=None
	try:
		text = request.form['text']
	except Exception as e:
		file = request.files['file']
	session["outPut"] = 'nothing'
	if not file and not text:
		return 'Error . must give file or text'
	if file:
	# get the file extension
		file_ext = file.filename.split('.')[-1]

		# save the file to server
		file.save('temp')

		text = files.readFile('temp', file_ext)

		os.remove('temp')

	result = plagiarismText(text=text, collegeId=session["college_id"], doerUserId=session['user_id'])

	if not result:
		return "can't plagiarism the Text"
	else:
		session["outPut"] = result

	# success
	return redirect(url_for('project', page_sec='outPut'))


@app.route("/", methods=['GET', 'POST'])
def login():
	""" log the user in """

	# Forget any user_id
	session.clear()

	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if not username:
			return 'user name missing' , 404
		elif not password:
			return 'password missing' , 404

		data = users.login(username, password)
		if data:
			# Remember which user has logged in
			session["user_id"]    		   	 = data[0]['id']
			session["user_name"]   		   	 = data[0]['name'].split(' ')[0]
			session["user_type"] 			 = data[0]['u_type']
			session["college_id"]			 = data[0]['college_id']
			if session["user_type"]!= 0:
				session["college_ plagiarism"]	 = colleges.getAllColleges(session["college_id"])[0]['plagiarism']
			else:
				session["college_ plagiarism"]	 =20.0

			return redirect(url_for('project'))
		else:
			return 'Rong username or password', 404
	
	else:
		allColleges = colleges.getAllColleges()
		return render_template('base.html', page='login', colleges=allColleges)

@app.route("/home")
@app.route("/home/<page_sec>")
@login_required
def project(page_sec=None):
	""" main page """

	# available sections
	sec = [  'colleges', 'researchs', 'users', 'outPut', 'newUsers', 'report','plagiarism','adminResets', None]

	# remember admin sections
	#admin_sec = sec[:5]

	# not found section
	if page_sec not in sec:
		return redirect('/404')

	# normal user try to access admin section
	#if session["user_type"] != 0 and page_sec in admin_sec:
	#	return redirect('/404')

	def getData():
		''' get the data that will passed to the templates depend on 'page_sec' '''

		# initialize some variables
		data = []

		# get the history if the admin want to viwe it
		if page_sec == 'report':
			data = history.report(session["college_id"])

		elif page_sec == 'newUsers':
			if session["user_type"] == 0:
				data = {'students' : history.getNotification(), 'colleges':colleges.getAllColleges()}
			else:
				data = {'students' :history.getNotification(session["college_id"]), 'colleges':colleges.getAllColleges(session["college_id"])}
			if not data['students']:
				data['students'] = []
			if not data['colleges']:
				data['colleges'] = []

		# get the books if the admin want to viwe it
		elif page_sec == 'researchs':
			
			if session["user_type"] == 0:
				data = {'researchs' : files.getAllFiles(), 'colleges':colleges.getAllColleges()}
			else:
				data = {'researchs' : files.getAllFiles(session["college_id"]), 'colleges':colleges.getAllColleges(session["college_id"])}

			if not data['researchs']:
				data['researchs'] = []
			if not data['colleges']:
				data['colleges'] = []


		elif page_sec == 'outPut':
			data = session["outPut"]
			#path = os.getcwd()
			#page = render_template('reportPdf.html', path=path, data=session["outPut"])
			#files.createPdf(page, 'out')
			#return page
			

		elif page_sec == 'colleges':
			data = colleges.getAllColleges()

		# get the users list if admin want to viwe them
		elif page_sec == 'users':
			if session["user_type"] == 0:
				data = {'users' : users.getAllUsers(), 'colleges':colleges.getAllColleges()}
			else:
				data = {'users' :users.getAllUsers(session["college_id"]), 'colleges':colleges.getAllColleges(session["college_id"])}
			if not data['users']:
				data['users'] = []
			if not data['colleges']:
				data['colleges'] = []
		if not data:
			data  =[]

		return data

	# if page_sec == 'users' and session["user_type"] == 1:
		# return str(getData())
	return render_template('base.html', page=page_sec, data=getData())


@app.route("/logout")
@login_required
def logout():
	''' logout the user'''
	session.clear()
	return redirect("/")

@app.route("/reset", methods=['POST'])
@login_required
def reset():
	''' reset the user password'''

	oldpass = request.form['oldpass']
	newpass = request.form['newpass']
	conpass = request.form['conpass']

	# check the feilds if sumbted
	if not oldpass:
		return 'old password missing' , 404
	elif not newpass:
		return 'new password missing' , 404
	elif not conpass:
		return 'confirm password must be sumbted', 404

	result = users.resetUserPassword(oldpass, newpass, conpass, session["user_id"])

	if not result:
		return "can't reset the password"
	elif result == True:
		pass
	else:
		return result

	return redirect("/logout")

@app.route("/adminResets", methods=['POST'])
@app.route("/adminResets/<userName>", methods=['GET'])
@login_required
def adminResets(userName=None):
	''' admin reset the user password'''
	if request.method == 'GET':
		return render_template('base.html', page='adminResets', selcted_user_username=userName)

	elif request.method == 'POST':

		username = request.form['username']
		newpass = request.form['password']
		conpass = request.form['confirmpassword']

		# check the feilds if sumbted
		if not username:
			return 'username missing' , 404
		elif not newpass:
			return 'new password missing' , 404
		elif not conpass:
			return 'confirm password must be sumbted', 404

		if newpass != conpass:
			return "the password don't mathch!", 404


		if not users.checkUsername(username):
			return "username Not found", 404

		if not users.updateUserPassword(username, newpass):
			return "can't change this user password"

		return redirect(url_for('project', page_sec='users'))

@app.route("/setprojectmanager/<userName>/<college>", methods=['GET'])
@login_required
def setproject(userName,college):
	''' admin reset the user password'''

	# check the feilds if sumbted
	if not userName:
		return 'username missing' , 404
	if not users.checkUsername(userName):
		return "username Not found", 404

	if not users.setprojectmanager(userName, college):
		return "can't set this user to project manager"

	return redirect(url_for('project', page_sec='users'))

@app.route("/blockUser/<block>/<userName>", methods=['GET'])
@login_required
def blockUser(userName=None, block=None):

	result = users.blockUser(userName, block)

	if not result:
		return "can't block the user"

	return redirect("/project/UserConfiguration")

@app.route("/adduser", methods=['POST'])
@login_required
def adduser():
	''' add new user '''

	studantID   = request.form['id']
	studantName = request.form['name']
	collegeID   = request.form['college']
	username    = request.form['username']
	email       = request.form['email']
	password    = request.form['password']
	conpassword = request.form['confirmpassword']

	# check the feilds if sumbted
	if not studantName:
		return 'studant name missing', 404
	if not validation(studantID, 'studantID'):
		return 'studant ID not correct'
	if not validation(email, 'email'):
		return 'email not correct'
	if not validation(username, 'username'):
		return 'username missing' , 404
	elif not validation(password, 'password'):
		return 'password missing' , 404
	elif not validation(conpassword, 'password') or password != conpassword:
		return 'confirm password must be sumbted', 404

	result = users.addNewUser(session['user_id'],studantName, username, password, 0, 2, studantID, collegeID, email)
	#addNewUser(doerUserId, name, userName, password, state , userType, universityId, collegeId, email)
	if not result:
		return "can't add the user"
	elif result == True:
		pass
	else:
		return result

	# success
	return redirect(url_for('project', page_sec='users'))

@app.route("/register", methods=['POST'])
def register():
	""" rigster new user """

	studantID   = request.form['id']
	studantName = request.form['name']
	collegeID   = request.form['college']
	username    = request.form['username']
	email       = request.form['email']
	password    = request.form['password']
	conpassword = request.form['confirmpassword']

	# check the feilds if sumbted
	if not studantName:
		return 'studant name missing', 404
	if not validation(studantID, 'studantID'):
		return 'studant ID not correct'
	if not validation(email, 'email'):
		return 'email not correct'
	if not validation(username, 'username'):
		return 'username missing' , 404
	elif not validation(password, 'password'):
		return 'password missing' , 404
	elif not validation(conpassword, 'password') or password != conpassword:
		return 'confirm password must be sumbted', 404

	result = users.rigesterNewUser(studantName, username, password, studantID, collegeID, email)
	if not result:
		return "can't rigster the user"
	elif result == True:
		pass
	else:
		return result

	# success
	return redirect("/")

@app.route("/addfile", methods=['POST'])
@login_required
def addfile():

	name    = request.form['name']
	aothor  = request.form['aothor']
	collegeId = request.form['college']
	date    = request.form['date']
	file    = request.files['file']
	# for i in request.form :
	# 	if i == '2' or i == '3' or i == '4':
	# 		aothor += ';' + request.form[i]

	# check the feilds if sumbted
	if not name:
		return 'name missing' , 404
	elif not aothor:
		return 'aothor missing' , 404
	elif not collegeId:
		return "college can't be embty", 404
	elif not date:
		return 'date must be sumbted', 404
	elif not file:
		return 'file must be sumbted', 404

	result = files.addNewFile(session['user_id'], name, aothor, date, file, collegeId)
	
	if result == True:
		pass
	elif not result:
		return "can't add the file"
	else:
		return result

	# success
	return redirect(url_for('project', page_sec='researchs'))

# this route used with ajax to check if userName exist or not
@app.route("/checkUsername/<value>", methods=['POST'])
def checkUsername(value=None):
	if users.checkUsername(value):
		return '.'
	return ''

@app.route("/addCollege", methods=['POST'])
@login_required
def addCollege():
	name = request.form['name']
	rate = request.form['rate']

	# check the feilds if sumbted
	if not name:
		return 'name must be sumbted' , 404

	# check the feilds if sumbted
	if not rate:
		return 'rate must be sumbted' , 404

	result = colleges.addNewCollege(name, rate)

	if result:
		# success
		return redirect(url_for('project', page_sec='colleges'))
	else:
		#failed
		return "cant't add college"

@app.route("/requests", methods=['POST'])
@login_required
def answerer_requests():
    userName = request.form['username']
    Type     = request.form['type']
    if Type == 'accept':
        users.answererRequests(userName, Type='accept')
    	
    else:
    	users.answererRequests(userName, Type='reject')

    return redirect(url_for('project', page_sec='newUsers'))

# @app.route("/404")
# @app.errorhandler(404)
# def page_not_found(e=None):
# 	if e:
# 		return redirect('/404')

# 	return render_template('404.html'), 404

def validation(value, Type):
	sections = ['username', "email", 'password', 'studantID']
	if Type not in sections:
		return False

	def empty(value):
		length = len(value)
		if length == 0:
			return False
		else:
			return length

	length = empty(value)
	# required fields
	if Type in sections[:]:
		if not length:
			return False

	if Type == 'studantID':
		if length != 8:
			return False
		if not str(value).isdigit():
			return False

	if Type == 'username':		
		if length < 3:
			return False

	if Type == "email":
		if str(value).find('@') == -1:
			return False
		if len(str(value).split('.')[-1]) < 3 :
			return False

	if Type == 'password':
		if length < 5 or length > 28:
			return False

	return True

if __name__ == "__main__":
	app.run(debug=1)

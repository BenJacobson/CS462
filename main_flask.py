from flask import Flask, redirect, request, make_response, send_from_directory, render_template
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask_sqlalchemy import SQLAlchemy
from foursquare import FourSquare
import binascii
import random
import types
import json
import ssl
import os

# Initialize application

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CS462.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
	
providers = {
    'foursquare': FourSquare
}

# Define database models

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	foursquareid = db.Column(db.Integer, unique=True)
	foursquaretoken = db.Column(db.String(50), unique=False)
	sessionid = db.Column(db.Integer, unique=True)
	firstname = db.Column(db.String(20), unique=False)
	lastname = db.Column(db.String(20), unique=False)
	email = db.Column(db.String(40), unique=True)
	
	def is_logged_in(self):
		return self.sessionid is not None
	
	def __repr__(self):
		return '<User {0} {1}>'.format(self.firstname, self.lastname)
		

# Helpful decorators

def validate_user(f):
	def validate_user_wrapper(*args, **kwargs):
		global current_user
		sessionid = request.cookies.get('session')
		current_user = User.query.filter_by(sessionid=sessionid).first() or User()
		kwargs['current_user'] = current_user
		return f(*args, **kwargs)
	validate_user_wrapper.__name__ = f.__name__
	return validate_user_wrapper


# Define routes

@app.route('/')
@validate_user
def home(current_user):
	all_users = User.query.all()
	return render_template('index.html', current_user=current_user, users=all_users)
	

@app.route('/login')
@validate_user
def login(current_user):
	if current_user.is_logged_in():
		return redirect('/')
	else:
		return render_template('login.html')
		
		
@app.route('/logout')
@validate_user
def logout(current_user):
	if current_user.sessionid is not None:
		current_user.sessionid = None
		db.session.commit()
	return redirect('/')

	
@app.route('/authorize/<provider>')
@validate_user
def oauth_authorize(provider, current_user):
	if provider in providers:
		return providers[provider].begin_oauth()
	else:
		return redirect('/')


@app.route('/callback/<provider>')	
def oauth_callback(provider):
	if provider in providers:
		access_token = providers[provider].authenticate()
		user_data = providers[provider].get_user_data(access_token)
		user = User.query.filter_by(foursquareid=user_data['id']).first()
		if user is None:
			user = User(
				foursquareid=user_data['id'],
				foursquaretoken=access_token,
				firstname=user_data['firstName'],
				lastname=user_data['lastName'],
				email=user_data['contact']['email'],
			)
			db.session.add(user)
		new_sessionid = binascii.hexlify(os.urandom(16))
		user.sessionid = new_sessionid
		db.session.commit()
		response = make_response(redirect('/'))
		response.set_cookie('session', new_sessionid)
		return response
	return redirect('/')
		

@app.route('/user/<id>')
@validate_user
def user_page(id, current_user):
	try:
		user = User.query.filter_by(id=id).one()
		checkins = FourSquare.get_checkins(user.foursquaretoken)
		return render_template('user.html', user=user, current_user=current_user, checkins=checkins)
	except NoResultFound:
		return 'NoResultFound'
	except MultipleResultsFound:
		return 'MultipleResultsFound'


@app.route('/chat')
@validate_user
def chat(current_user):
	return render_template('chat.html', current_user=current_user)


forwarding_store = dict()

@app.route('/gossip/<uuid>', methods=['POST'])
@validate_user
def gossip(current_user, uuid):
	global forwarding_store
	if uuid not in forwarding_store:
		forwarding_store[uuid] = []
	if not current_user.is_logged_in():
		response = make_response()
		response.headers['Content-Type'] = 'application/json'
		response.data = '{"error": {"message": "please login to chat"}}'
		return response
	data = request.get_data()
	other_user = random.sample(forwarding_store.keys(), 1)[0]
	if other_user != uuid:
		forwarding_store[other_user].insert(0, data)
	# return pending items sent to user
	return forwarding_store[uuid].pop() if len(forwarding_store[uuid]) > 0 else ''

	
def create_append_function():
	def append_function(self, text):
		self.data += text + '\n\r'
	return append_function
	
	
@app.route('/dump', methods=['GET', 'POST'])
def dump():
	response = make_response()
	response.append = types.MethodType(create_append_function(), response)
	response.mimetype = 'text/plain'
	response.append('Request Headers')
	for header in request.headers:
		response.append('  {0}: {1}'.format(header[0], header[1]))
	response.append('Query string parameters')
	for a in request.args:
		response.append('  {0} = {1}'.format(a, request.args[a]))
	response.append('Request Body')
	response.append('  ' + request.get_data())
	return response
	
	
@app.route('/redirect')
def my_redirect():
	if 'google' in request.args:
		return redirect('https://www.google.com')
	elif 'byu' in request.args:
		return redirect('http://www.byu.edu')
	elif 'ksl' in request.args:
		return redirect('https://www.ksl.com')
	elif 'lds' in request.args:
		return redirect('https://www.lds.org')
	else:
		return redirect('/')

		
@app.route('/accept')
def acccept():
	response = make_response()
	response.headers['Content-Type'] = 'application/json'
	if 'Accept' in request.headers:
		accept_header = request.headers['Accept']
		if accept_header == 'application/vnd.byu.cs462.v1+json':
			response.data = '{"version": "v1" }'
			return response
		elif accept_header == 'application/vnd.byu.cs462.v2+json':
			response.data = '{"version": "v2" }'
			return response
	response.data = '{"error": {"message": "Accept header not recognized"}}'
	return response

	
@app.route('/<filename>')
def static_files(filename):
	return send_from_directory('static', filename);


# Run application

if __name__ == '__main__':
	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
	context.load_cert_chain('cert.pem', 'key.pem')
	app.run(host='0.0.0.0', port=443, ssl_context=context)

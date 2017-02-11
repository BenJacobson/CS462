from flask import Flask, redirect, request, make_response, send_from_directory, render_template
from foursquare import FourSquare
from flask_sqlalchemy import SQLAlchemy
import types
import ssl

# Initialize application

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CS462.db'
db = SQLAlchemy(app)
	
providers = {
    'foursquare': FourSquare
}


# initialize database

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	foursquareid = db.Column(db.Integer, unique=True)
	sessionid = db.Column(db.Integer, unique=True)
	firstname = db.Column(db.String(20), unique=True)
	lastname = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(40), unique=True)
	
	def __repr__(self):
		return '<User {0} {1}>'.format(self.firstname, self.lastname)


# Define routes

@app.route('/')
def home():
	return render_template('index.html')
	
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if provider in providers:
		if 'code' in request.args:
			access_token = providers[provider].authenticate(request.args.get('code'))
			user = providers[provider].get_user_data(access_token)
			response = make_response()
			response.data += repr(user)
			return response
		else:
			return providers[provider].begin_oauth()
	else:
		return redirect('/')
	
	
def create_append_function():
	def append_function(self, text):
		self.data += text + '\n\r'
	return append_function
	
	
@app.route('/dump', methods = ['GET', 'POST'])
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
	response.headers[''] = 'application/json'
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


if __name__ == '__main__':
	context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
	context.load_cert_chain('cert.pem', 'key.pem')
	app.run(host='0.0.0.0', port=443, ssl_context=context)

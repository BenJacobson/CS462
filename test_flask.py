from flask import Flask, redirect, request, make_response, send_from_directory
import types
app = Flask(__name__)

@app.route('/')
def lab1():
	return send_from_directory('static', 'Lab1.txt');
	
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
	return 'accept'

@app.route('/<filename>')
def static_files(filename):
	return send_from_directory('static', filename);

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)

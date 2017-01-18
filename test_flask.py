from flask import Flask
app = Flask(__name__)
	
@app.route('/')
def hello_world():
    return 'Ben Jacobson - CS462'

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)

from flask import redirect
import requests
import json


class FourSquare:

	_CLIENT_ID = 'GPWFUYGOJBMASF0CAMEYEPQTQCHWOCSRFQEJYVGTIYG3L01D'
	_CLIENT_SECRET = 'VD5YTEAN2SKZAEI1GLMBPKOSE2YXR3BAKP1RP41M4Q1PONZH'
	_REDIRECT_URL = 'https://ec2-52-25-168-24.us-west-2.compute.amazonaws.com/authorize/foursquare'

	@classmethod
	def begin_oauth(cls):
		return redirect(
				'https://foursquare.com/oauth2/authenticate' +
					'?client_id={0}'.format(cls._CLIENT_ID) +
					'&response_type=code' +
					'&redirect_uri={0}'.format(cls._REDIRECT_URL)
			)
		
	@classmethod
	def authenticate(cls, code):
		json_response = requests.get(
			'https://foursquare.com/oauth2/access_token' +
				'?client_id={0}'.format(cls._CLIENT_ID) +
				'&client_secret={0}'.format(cls._CLIENT_SECRET) +
				'&grant_type=authorization_code' +
				'&redirect_uri={0}'.format(cls._REDIRECT_URL) +
				'&code={0}'.format(code)
		).content
		access_token = json.loads(json_response)['access_token']
		return access_token
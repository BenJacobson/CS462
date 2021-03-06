from flask import redirect, request
import requests
import json


class FourSquare:

	_CLIENT_ID         = 'GPWFUYGOJBMASF0CAMEYEPQTQCHWOCSRFQEJYVGTIYG3L01D'
	_CLIENT_SECRET     = 'VD5YTEAN2SKZAEI1GLMBPKOSE2YXR3BAKP1RP41M4Q1PONZH'
	_REDIRECT_URL      = 'https://ec2-52-25-168-24.us-west-2.compute.amazonaws.com/callback/foursquare'
	_AUTHENTICATE_URL  = 'https://foursquare.com/oauth2/authenticate'
	_ACCESS_TOKEN_URL  = 'https://foursquare.com/oauth2/access_token'
	_USER_DATA_URL     = 'https://api.foursquare.com/v2/users/self'
	_USER_CHECKINS_URL = 'https://api.foursquare.com/v2/users/self/checkins'
	_VERSION = '20170902'
	
	@classmethod
	def begin_oauth(cls):
		return redirect(
				cls._AUTHENTICATE_URL +
				'?client_id={0}'.format(cls._CLIENT_ID) +
				'&response_type=code' +
				'&redirect_uri={0}'.format(cls._REDIRECT_URL)
			)
		
	@classmethod
	def authenticate(cls):
		code = request.args.get('code')
		url = cls._ACCESS_TOKEN_URL + \
				'?client_id={0}'.format(cls._CLIENT_ID) + \
				'&client_secret={0}'.format(cls._CLIENT_SECRET) + \
				'&grant_type=authorization_code' + \
				'&redirect_uri={0}'.format(cls._REDIRECT_URL) + \
				'&code={0}'.format(code)
		json_response = requests.get(url).content
		access_token = json.loads(json_response)['access_token']
		return access_token
		
	@classmethod
	def get_user_data(cls, access_token):
		url = cls._USER_DATA_URL + \
				'?oauth_token={0}'.format(access_token) + \
				'&v={0}'.format(cls._VERSION)
		json_response = requests.get(url).content
		foursquare_user = json.loads(json_response)['response']['user']
		return foursquare_user

	@classmethod
	def get_checkins(cls, access_token):
		url = cls._USER_CHECKINS_URL + \
				'?oauth_token={0}'.format(access_token) + \
				'&v={0}'.format(cls._VERSION)
		json_response = requests.get(url).content
		checkins = json.loads(json_response)
		return checkins['response']['checkins']

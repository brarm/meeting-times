#!/usr/bin/python
import os
import json

import flask
import httplib2

from apiclient import discovery
import oauth2client 
from oauth2client import client
from oauth2client import tools

import datetime

app = flask.Flask(__name__)

@app.route('/')
def index():
	if 'credentials' not in flask.session:
		return flask.redirect(flask.url_for('oauth2callback'))
	credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
	if credentials.access_token_expired:
		return flask.redirect(flas.url_for('oauth2callback'))
	else:
		http_auth = credentials.authorize(httplib2.Http())
		service = discovery.build('calendar', 'v3', http=http_auth)
		eventsResult = service.events().list(
			calendarId='primary', 
			timeMax='2015-11-22T00:00:00Z',
			timeMin='2015-11-15T00:00:00Z',
			fields='items(attendeesOmitted,end,id,originalStartTime,recurrence,recurringEventId,source,start,summary)').execute()
		events = eventsResult.get('items', [])

		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			print(start, event['summary'])

		return 'test'

SCOPES='https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE='client_secrets.json'
APPLICATION_NAME='Meeting Times'
INCLUDE_GRANTED_SCOPES=True

@app.route('/oauth2callback')
def oauth2callback():
	flow = client.flow_from_clientsecrets(
		CLIENT_SECRET_FILE, 
		SCOPES, 
		redirect_uri=flask.url_for('oauth2callback', _external=True))
	if 'code' not in flask.request.args:
		auth_uri = flow.step1_get_authorize_url()
		return flask.redirect(auth_uri)
	else:
		auth_code = flask.request.args.get('code')
		credentials = flow.step2_exchange(auth_code)
		flask.session['credentials'] = credentials.to_json()
		return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
	import uuid
	app.secret_key = str(uuid.uuid4())
	app.debug = True
	app.run()
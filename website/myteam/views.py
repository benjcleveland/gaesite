#!/usr/bin/python

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import gdata.alt.appengine
import gdata.calendar.data
import gdata.calendar.client
import atom
import time

import urllib2
import urllib

from models import LoginForm, googLoginForm

import team_cowboy

def index( request ):

    if request.method == 'POST':
        # user entered login information
        login_form = LoginForm( request.POST )
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            tc_api = team_cowboy.TeamCowboyApi()
            try:
                # try to login
                login = tc_api.team_cowboy_login(username, password)
            except urllib2.HTTPError:
                # assume a failure means that the username and password is in correct
                message = 'Invalid username or password!'
                login_form = LoginForm()
                return render_to_response('myteam/index.html', { 'title' : 'Login', 'message' : message, 'login_form':login_form }, context_instance=RequestContext(request))

            try:
                teamids = tc_api.team_cowboy_get_teamid( login['body']['token'] )
                teams = tc_api.team_cowboy_get_team_members(login['body']['token'], teamids )
            except urllib2.HTTPError,e:
                message = 'Error getting data from team cowboy...'
                return render_to_response('myteam/index.html', { 'title' : 'Login', 'message' : message, 'login_form':login_form }, context_instance=RequestContext(request))

            message = 'Displaying results for user ' +  str(username)

            return render_to_response('myteam/index.html', { 'team_info': teams, 'title' : 'Contact lists from team cowboy', 'message' : message})
        else:
            return render_to_response('myteam/index.html', { 'title' : 'Login', 'message' : 'Enter your team cowboy username and password', 'login_form':login_form }, context_instance=RequestContext(request))
    else:
        # must be a get
        login = LoginForm()
        message = 'Enter your team cowboy username and password.'
        return render_to_response('myteam/index.html', { 'title' : 'Login', 'message' : message, 'login_form':login }, context_instance=RequestContext(request))

#    return HttpResponse( str(teams) ) 


def update_calendar( request ):

    if request.method == 'POST':
        login_form = googLoginForm( request.POST )

        if login_form.is_valid():
            tc_username = login_form.cleaned_data['team_cowboy_username']
            tc_password = login_form.cleaned_data['team_cowboy_password']
            goog_username = login_form.cleaned_data['google_username']
            goog_password = login_form.cleaned_data['google_password']

            tc_api = team_cowboy.TeamCowboyApi()
            login = tc_api.team_cowboy_login( tc_username, tc_password)

            teamids = tc_api.team_cowboy_get_teamid( login['body']['token'] )
            
            games = tc_api.team_cowboy_get_team_schedule( login['body']['token'], teamids ) 


            # connect to google calendar
            client = gdata.calendar.client.CalendarClient(source='ben-cleveland-schedule-updater_1.0')
            #gdata.alt.appengine.run_on_appengine(client)
            client.ClientLogin( goog_username, goog_password, client.source)
            '''  
            for game in games:
                event = gdata.calendar.data.CalendarEventEntry()
                event.title = atom.data.Title(text=game['title'])
                event.content = atom.data.Content(text=game['content'])
                event.where.append(gdata.data.Where(value=game['content']))

                # Use current time for the start_time and have the event last 1 hour
                end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z',
                    time.gmtime(time.time() + 3600))
                start_time = game['starttime'].replace(' ','T')
                end_time = game['endtime'].replace(' ','T')
                event.when.append(gdata.data.When(start=start_time,
                    end=end_time))

                new_event = client.InsertEvent(event)
                #new_event = client.Update(event)
            '''
            #message = 'Your google calendar has been updated with your team cowboy schedule'
            message = 'This is not yet implemented'
            return render_to_response('myteam/calendar.html', {'title' : 'Updated Schedule', 'message' : message}, context_instance=RequestContext(request))
    else:
        login = googLoginForm()
        message = 'Enter your login information.  Hitting submit will update your google calendar with your team cowboy game schedule'
        return render_to_response('myteam/calendar.html', {'title' : 'Login', 'message' : message, 'login_form' : login }, context_instance=RequestContext(request))
    


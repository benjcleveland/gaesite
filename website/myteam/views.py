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
              
            # get all the events on the default calendar
            feed = client.GetCalendarEventFeed()
            
            # get a list of the events
            events = [ event.title.text for i, event in zip(xrange(len(feed.entry)), feed.entry) ]

            # create a feed to hold all the batch request entries
            batch_feed = gdata.calendar.data.CalendarEventFeed()
            for game in games:
                # build the start and end times
                start_time = game['starttime'].replace(' ','T')
                end_time = game['endtime'].replace(' ','T')

                title = game['team_name'] + ' vs. ' + game['opponent']
                # check to see if this game is already on the calendar
                if title not in events:
                    # add this event
                    event = gdata.calendar.data.CalendarEventEntry()
                    event.title = atom.data.Title(text=title)
                    event.content = atom.data.Content(text=game['content'])
                    event.where.append(gdata.data.Where(value=game['content']))


                    event.when.append(gdata.data.When(start=start_time,
                        end=end_time))

                    event.batch_id = gdata.data.BatchId(text=title)
                    batch_feed.AddInsert(entry=event)

                    #new_event = client.InsertEvent(event)
                    #new_event = client.Update(event)

            # submit the batch request to the server
            response_feed = client.ExecuteBatch(batch_feed, gdata.calendar.client.DEFAULT_BATCH_URL)

            message = 'Your google calendar has been updated with your team cowboy schedule'
            return render_to_response('myteam/calendar.html', {'title' : 'Updated Schedule', 'message' : message, 'feed':events, 'batch_results' : response_feed.entry}, context_instance=RequestContext(request))

    else:
        login = googLoginForm()
        message = 'Enter your login information.  Hitting submit will update your google calendar with your team cowboy game schedule'
        return render_to_response('myteam/calendar.html', {'title' : 'Login', 'message' : message, 'login_form' : login }, context_instance=RequestContext(request))
    


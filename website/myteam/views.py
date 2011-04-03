#!/usr/bin/python

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from google.appengine.api import urlfetch

import urllib2
import urllib
import time
import hashlib 
import sys
#import json

import team_cowboy

from models import LoginForm


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


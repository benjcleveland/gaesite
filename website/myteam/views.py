#!/usr/bin/python

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import urllib2
import urllib
import time
import hashlib 
import json
import sys

sys.path.append('/home/cleveb/keys/')
import cowboy_keys

from models import LoginForm

def build_url( method ):
    
    url_dict = { 'api_key' : cowboy_keys.PUBLIC_KEY,
                'method' : method,
                'nonce' : str(time.time()),
                'timestamp' : str(int(time.time())),
                'response_type' : 'json',
    }
    
    return url_dict

def create_url_string( url_dict ):
    '''
    create a sorted url form the dictionary
    '''
    url_string = ''
    for key in sorted( url_dict.iterkeys()):
       url_string = '&'.join([url_string, '='.join([key ,urllib.quote(url_dict[key])])])
    return url_string[1:]

def create_sig( url_dict, req_type ):
    '''
    create the sig portion of the request and save it in the url dict
    '''

    p_api_key = cowboy_keys.PRIVATE_KEY 

    url_string = create_url_string(url_dict).lower()
    sig_string = '|'.join([p_api_key, req_type, url_dict['method'], url_dict['timestamp'], url_dict['nonce'],url_string])

    # create the hash
    h = hashlib.sha1( sig_string ).hexdigest()

    # save it
    url_dict['sig'] = h


def team_cowboy_test( test_string ):
    
    url_dict = build_url('Test_GetRequest')

    url_dict['testParam'] = test_string
    
    # create the sig
    create_sig( url_dict, 'GET')

   # url_dict = sorted(url_dict, key=url_dict.iterkeys())
    request = create_url_string(url_dict)
    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('http://api.teamcowboy.com/v1/?' + request, headers=headers)
    res = urllib2.urlopen(url)
    data = res.read()


def team_cowboy_test_post( test_string ):

    url_dict = build_url('Test_PostRequest')
    url_dict['testParam'] = test_string

    create_sig( url_dict, 'POST')

    request = create_url_string(url_dict)

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('http://api.teamcowboy.com/v1/', data=request, headers=headers)
    res = urllib2.urlopen(url)
    data = res.read()

def team_cowboy_login( username, password ):

    url_dict = build_url('Auth_GetUserToken')
    url_dict['username'] = username
    url_dict['password'] = password

    # create sig
    create_sig( url_dict, 'POST')

    request = create_url_string( url_dict )

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('https://api.teamcowboy.com/v1/', data=request, headers=headers)
    res = urllib2.urlopen(url)

    data = json.loads( res.read())

    return data



def team_cowboy_get_teamid( usertoken ):

    url_dict = build_url('User_GetTeams')
    url_dict['userToken'] = usertoken 

    # create sig
    create_sig( url_dict, 'GET')

    request = create_url_string( url_dict )

    headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
    url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
    res = urllib2.urlopen(url)

    data = json.loads( res.read())

    ids = []
    for value in data['body']:
        ids.append((value['name'],value['teamId']))
    return ids 

def team_cowboy_get_team_members(usertoken,  teamid ):

    name_list = [] 

    for (name,team) in teamid:

        url_dict = build_url('Team_GetRoster')
        url_dict['userToken'] = usertoken 
        url_dict['teamId'] = team
        url_dict['userId'] = ''
        url_dict['includeInactive'] = 'False'
        url_dict['sortBy'] = ''
        url_dict['sortDirection'] = '' 

        # create sig
        create_sig( url_dict, 'GET')

        request = create_url_string( url_dict )

        headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}
        url = urllib2.Request('https://api.teamcowboy.com/v1/?' + request, headers=headers)
        res = urllib2.urlopen(url)

        data = json.loads( res.read())
        data['teamname'] = name
        name_list.append (data)

    return name_list 


def index( request ):
    
    if request.method == 'POST':
        # user entered login information
        login_form = LoginForm( request.POST )
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']

            try:
                # try to login
                login = team_cowboy_login(username, password)
            except urllib2.HTTPError:
                # assume a failure means that the username and password is in correct
                message = 'Invalid username or password!'
                login_form = LoginForm()
                return render_to_response('myteam/index.html', { 'title' : 'Login', 'message' : message, 'login_form':login_form }, context_instance=RequestContext(request))

            try:
                teamids = team_cowboy_get_teamid( login['body']['token'] )
                teams = team_cowboy_get_team_members(login['body']['token'], teamids )
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

if __name__ == '__main__':
# test stuff - not normaly executed
# login
    team_cowboy_test( 'Ben is')
    team_cowboy_test_post( 'Ben is')
    login = team_cowboy_login('', '')
    teamids = team_cowboy_get_teamid( login['body']['token'] )
    team_cowboy_get_team_members(login['body']['token'], teamids )


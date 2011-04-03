# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import Http404
from django.db.models import Avg
from django.template import RequestContext
from django.contrib.auth import authenticate, login

from decimal import *
from operator import itemgetter
from gameviewer.models import Game, Rating, RatingForm
import datetime
import os

# helper function
def get_average( game ):
    '''
    Return the average game rating to two decimal places
    '''
    getcontext().prec = 3    
    avg = {}

    ratings = Rating.objects.filter( game=game.id )
    total = 0.0 
    for rate in ratings:
        total += float(rate.rating)
        
    if len( ratings ) > 0:
        avg['rating__avg'] = ('%0.2f' % (total/len(ratings)))
    else:
        avg['rating__avg'] = None
    return avg 

def index(request):
    '''
    Display all the games we currently have
    '''
    latest_game_list = Game.objects.all().order_by('title')
    return render_to_response('gameviewer/index.html', {'latest_game_list':latest_game_list, 'title':'Welcome to my Board Game Collection!'})

def about(request):

    return render_to_response('gameviewer/about.html', {'title':'My board game collection'})

def top(request):
    '''
    display the top 10 rated games
    '''
    # get all the games
    latest_game_list = Game.objects.all()

    top_list = [] 
    for game in latest_game_list:
        # create a list of dictionaries with teh average rating for each game
        top_list.append({'title':game.title, 'id':game.id, 'average_rating':get_average(game)['rating__avg']})

    # sort the games by rating and only take the top 10
    top_list = sorted(top_list, key=itemgetter('average_rating'), reverse=True)[:10] 

    return render_to_response('gameviewer/index.html', {'latest_game_list':top_list, 'title':'Top 10 Rated board games'})

def user_top(request):
    '''
    display the top 10 games per user
    '''

    names = Rating.objects.values('name').order_by('name')

    # remove duplicates
    dict_names = {}
    for name in names:
        dict_names[name['name']] = name['name']
    
    top_rated_games = [] 
    for name in dict_names:
        top_rated_games.append( ( name, Rating.objects.filter(name=name).order_by('rating').reverse()[:10]))
        
    return render_to_response('gameviewer/user.html', {'latest_game_list':top_rated_games, 'title':'Top 10 rated board games by user'})
    return HttpResponse( top_rated_games  )
    
def detail(request, game_id):
    '''
    Display details about the game
    '''

    # get the game object
    g = get_object_or_404(Game, pk=game_id)

    # determine the game average rating
    average = get_average(g)

    # create the form
    form = RatingForm()

    return render_to_response('gameviewer/detail.html', {'game': g, 'average_rating': average, 'rating_form':form,}, context_instance=RequestContext(request) )

def rate(request, game_id):
    '''
    add a rating to a game
    '''

    game = get_object_or_404(Game, pk=game_id)
    average = get_average(game)
    rating_form = RatingForm(request.POST)

    if rating_form.is_valid():

        name = rating_form.cleaned_data['name'].strip()
        comment = rating_form.cleaned_data['comment'].strip()
        rating = rating_form.cleaned_data['rating']

        r = game.rating_set.create(rating=rating, name=name, comment=comment)
        game.save()

        average = get_average(game)

        return render_to_response('gameviewer/detail.html', {'game': game, 'average_rating':average }, context_instance=RequestContext(request) )
    else:
        return render_to_response('gameviewer/detail.html', {'game': game, 'average_rating':average, 'rating_form': rating_form }, context_instance=RequestContext(request) )

def list(request, game_id, search):
    '''
    filter games based on a specific type (search)
    '''

    g = get_object_or_404(Game, pk=game_id)
    
    search_dict = { 'publisher' : 'Games published by ' + g.publisher,
        'genre' : 'Games in the ' + g.genre + ' genre',
        'max' : 'Games that support at least ' + str(g.maxplayers) + ' players', 
        'min' : 'Games that support at least ' + str(g.minplayers) + ' players',
        'year' :'Games published in ' +  g.year_published,
    }

    # TODO - figure out a better way to do this
    if search == 'publisher':
        games = get_list_or_404(Game, publisher=g.publisher)
    elif search == 'genre':
        games = get_list_or_404(Game, genre=g.genre)
    elif search == 'max':
        games = get_list_or_404(Game, maxplayers__gte=g.maxplayers)
    elif search == 'min':
        games = get_list_or_404(Game, minplayers__lte=g.minplayers)
    elif search == 'year':
        games = get_list_or_404(Game, year_published=g.year_published)
    else:
        games = []

    # create the page title
    title = (search_dict.get(search,''))
    
    return render_to_response('gameviewer/index.html', {'latest_game_list': games, 'title':title}) 

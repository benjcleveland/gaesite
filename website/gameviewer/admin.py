from gameviewer.models import Game 
from django.contrib import admin
from gameviewer.models import Rating

class GameAdmin( admin.ModelAdmin ):
    list_display = ('title', 'publisher', 'last_played' )

class RatingAdmin( admin.ModelAdmin ):
    list_display = ('game', 'rating')

admin.site.register(Rating, RatingAdmin)
admin.site.register(Game, GameAdmin)

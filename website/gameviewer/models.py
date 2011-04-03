from django.db import models
from django import forms


class RatingForm(forms.Form):
    name = forms.CharField(max_length=20)
    rating = forms.DecimalField( max_value=10, min_value=0)
    comment = forms.CharField(max_length=144, required=False, widget=forms.Textarea( attrs={'rows':"4", 'cols':"30"}))

# Create your models here.
class Game(models.Model):

    def __unicode__(self):
        return str(self.title)

    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    year_published = models.CharField(max_length=4)
    description = models.CharField(max_length=400)
    last_played = models.DateTimeField('last played')
    image_name = models.CharField(max_length=200)
    genre = models.CharField(max_length=100)
    maxplayers = models.IntegerField()
    minplayers = models.IntegerField()
    #image = models.FileField(upload_to='images', max_length=500 )

class Rating(models.Model):
    
    def __unicode__(self):
        return str(self.rating)
    
    game = models.ForeignKey(Game)
    rating = models.DecimalField( max_digits=3, decimal_places=1)
    name = models.CharField(max_length=20)
    comment = models.CharField(max_length=144, default='')

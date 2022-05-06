from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profile(models.Model): # a user profile # when a new user is created
    first_name = models.CharField(max_length=200,blank=True)
    last_name = models.CharField(max_length=200,blank=True)
    email = models.EmailField(max_length=300,blank=True)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # one to one to the user entity
    # the user that comes with django # associating each profile to a user, once we know a user, we can get their profile.
    friends = models.ManyToManyField(User,blank=True, related_name='friends') # a profile can have many friends # many to many with the user entity
    created = models.DateTimeField(auto_now=True) # date the profile was created
    updated = models.DateTimeField(auto_now_add=True) # date the profile was updated


    def __str__(self):
        return f"{self.user.username}" # returns the username from the user # Johnny Bhojwani, not profb.

STATUS_CHOICES = (
    ('sent','sent'),
    ('accepted','accepted')
)

class Relationship(models.Model): # establish relationship between two profiles
    # sender sends a friend request, the receiver is someone else in the network that we want to be friends with
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender') # FK to the profile class
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver') # FK to the profile class
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="sent") # when we first create the relationship, one the request is accepted, the status changes to accepted
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    

class Post(models.Model):
    description = models.CharField(max_length=255, blank=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE) # FK to the user entity
    image = models.ImageField(upload_to='images',blank=True) 
    # images uploaded by users will be saved in this folder # blank=true because not required to have an image 
    # # only works if pillow installed
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description # returns the description of the post

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE) # know what post the comment is associated to # FK to the post class
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE) # username is FK to user, know who is commenting
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return self.text
    
    
class Like(models.Model): # keep track of how many likes to a post
	username = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
	post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE) # who liked it and what post they liked



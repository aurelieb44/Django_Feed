from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required # decorator: function that runs to do verifications, once it's true, it can access the appropriate functions
# prevents unauthorized access to pages. # we don't want that for the home page
# # makes sure the only people that can access that function are the people that have logged in.
def profile(request):
    profile = Profile.objects.filter(user=request.user) 
    # refers to the person logged on to the system # user is one of the fields/attributes in the profile model
    # filter instead of get because get doesn't work with exist
    if not profile.exists(): # if the profile doesn't exist, create a profile for them
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) # load the page

    if request.method != 'POST':
        form = ProfileForm(instance=profile) # we want to load that instance of the user, not a blank form
    else: # the request method is paused, we are trying to save to the database
        form = ProfileForm(instance=profile, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile')

    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)

@login_required 
def myfeed(request):
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') 
    # grab all the posts that belong to a certain user # descending order by date
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() # number of comments linked to this post
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    # pass that information to context by zipping
    zipped_list = zip(posts, comment_count_list, like_count_list)
    
    context = {'posts': posts, 'zipped_list': zipped_list}
    return render(request, 'FeedApp/myfeed.html', context)

@login_required 
def new_post(request):
    # process the form based on whether get or post request
    if request.method != 'POST':
        form = PostForm() # load the post as a blank form
    else:
        form = PostForm(request.POST, request.FILES) 
        # getting everything from the form that is on the website, which is coming through this post request
        # request.FILES to get the image that come with the post
        if form.is_valid():
            new_post = form.save(commit=False) # attach the username to it before we save it # create an instance, we save it, but we don't write it to the database yet
            new_post.username = request.user
            new_post.save()
            return redirect('FeedApp:myfeed') # keep it at the same location so they can see their post
    context = {'form': form}
    return render(request, 'FeedApp/new_post.html', context) 

@login_required 
def comments(request, post_id): # want to see if someone has clicked on the comment button 
    # we are not using a form 
    # alternate way to get the information into the database, process it manually rather than having python to process it through a form
    if request.method == 'POST' and request.POST.get('btn1'): # check if request method is post and if submit button was clicked
    # the second part of and will result to true or false
    # by naming the elements, we can get the corresponding value
        comment = request.POST.get("comment") # getting whatever text is in that box
        Comment.objects.create(post_id=post_id, username=request.user, text=comment, date_added=date.today()) # create a new row in the comment table
    
    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id) # refresh the page: get the comment from the database to display on the screen #Comment is the model
    context = {'post':post, 'comments':comments}

    return render(request, 'FeedApp/comments.html', context)

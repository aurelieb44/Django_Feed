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
    profile = Profile.objects.filter(user=request.user) # see if it exists using filter
    # request.user: refers to the person logged on to the system 
    # # user is one of the fields/attributes in the profile model
    # filter instead of get because get doesn't work with exist
    if not profile.exists(): # if the profile doesn't exist, create a profile for them
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) # load the page # get the actual profile

    if request.method != 'POST':
        form = ProfileForm(instance=profile) # we want to load that instance of the user, not a blank form
        # ProfileForm is a model in forms.py
    else: # the request method is post, we are trying to save to the database
        form = ProfileForm(instance=profile, data=request.POST)  # save the data coming from the webpage
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile') # redirect the user to the profile page.

    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)

@login_required 
def myfeed(request):
    comment_count_list = []
    like_count_list = []
    posts = Post.objects.filter(username=request.user).order_by('-date_posted') # Post refers to the model in models.py
    # grab all the posts that belong to a certain user # descending order by date
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() # number of comments linked to this post
        l_count = Like.objects.filter(post=p).count()
        print(l_count)
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    # pass that information to context by zipping, having both the number of comments and likes for the post p.
    zipped_list = zip(posts, comment_count_list, like_count_list)
    
    context = {'posts': posts, 'zipped_list': zipped_list}
    return render(request, 'FeedApp/myfeed.html', context) # rend to the myfeed page

@login_required 
def new_post(request):
    # process the form based on whether get or post request
    if request.method != 'POST':
        form = PostForm() # if it's not a post request, load the post as a blank form
    else:
        form = PostForm(request.POST, request.FILES) 
        # getting everything from the form that is on the website, which is coming through this post request
        # request.FILES to get the image that come with the post
        if form.is_valid():
            new_post = form.save(commit=False) # create an instance, we save it, but we don't write it to the database yet
            new_post.username = request.user # attach the username to it before we save it 
            new_post.save() # save
            return redirect('FeedApp:myfeed') # keep it at the same location so they can see their post
    context = {'form': form}
    return render(request, 'FeedApp/new_post.html', context) 

@login_required 
def friendsfeed(request):
    comment_count_list = []
    like_count_list = []
    friends = Profile.objects.filter(user=request.user).values('friends')
    #posts = Post.objects.filter(username=request.user).order_by('-date_posted') 
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted') 
    # grab all the posts that belong to a certain user # descending order by date
    for p in posts:
        c_count = Comment.objects.filter(post=p).count() # number of comments linked to this post
        l_count = Like.objects.filter(post=p).count()
        comment_count_list.append(c_count)
        like_count_list.append(l_count)
    # pass that information to context by zipping
    zipped_list = zip(posts, comment_count_list, like_count_list)

    if request.method == 'POST' and request.POST.get("like"): 
        # check if the like button is clicked # give the actual button name from friendsfeed.html to get the value and know if it was pressed.
        post_to_like = request.POST.get("like")
        print(post_to_like)
        like_already_exists = Like.objects.filter(post_id=post_to_like, username=request.user) 
        # don't want the person to like more than once
        if not like_already_exists.exists(): # exists is the name of the function that checks for it
            Like.objects.create(post_id=post_to_like, username=request.user)
            return redirect("FeedApp:friendsfeed")

    
    context = {'posts': posts, 'zipped_list': zipped_list}
    return render(request, 'FeedApp/friendsfeed.html', context)

@login_required 
def comments(request, post_id): # want to see if someone has clicked on the comment button 
    # we are not using a form 
    # alternate way to get the information into the database, process it manually rather than having python to process it through a form
    if request.method == 'POST' and request.POST.get('btn1'): # check if request method is post and if submit button was clicked
    # the second part of and will result to true or false
    # by naming the elements, we can get the corresponding value
        comment = request.POST.get("comment") # getting whatever text is in that box
        Comment.objects.create(post_id=post_id, username=request.user, text=comment, date_added=date.today()) 
        # create a new row in the comment table
    
    comments = Comment.objects.filter(post=post_id) # get all the comments for a particular post when refreshing the page
    post = Post.objects.get(id=post_id) # know which post the comment is referring to
    context = {'post':post, 'comments':comments}

    return render(request, 'FeedApp/comments.html', context)

@login_required
def friends(request):
    # get the admin profile and user profile to create the first relationship
    admin_profile = Profile.objects.get(user=1) # id=1 because first user ever created is the admin
    user_profile = Profile.objects.get(user=request.user)

    # to get the friends # friends is a collection of users
    user_friends = user_profile.friends.all() # gives a list of users
    # friends is from the Profile model and is a collection of user
    user_friends_profiles = Profile.objects.filter(user__in=user_friends) # filter it for the profile objects
    # gives a list of user friends for profiles. # the profiles of each of my user friends, this will be a list I can iterate through.

    # to get list of friend requests sent # the sender is the profile of the user
    user_relationships = Relationship.objects.filter(sender=user_profile) # people the user has sent requests to # filter based on the sender 
    request_sent_profiles = user_relationships.values('receiver') # collection of profiles that we sent a request to
    # the receiver is a Profile object in the Relationship class. # grab the receiver of the object

    # to get eligible profiles: exclude user, their existing friends, and friend requests sent already
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)

    # to get friend requests received by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent')

    # if this is the first time to access the friend requests page, create the first relationship
    # with the admin of the website (so the admin is friends with everyone)

    if not user_relationships.exists(): # if there aren't any relationships # 'filter' works with exists, 'get' doesn't
        Relationship.objects.create(sender=user_profile, receiver=admin_profile, status='sent') # the sender is a profile object
        #relationship = Relationship.objects.filter(sender=user_profile, status='sent')

    # check to see which submit button was pressed (sending a friend request or accepting a friend request)

    # this is to process all friend requests
    if request.method == 'POST' and request.POST.get("send_requests"): # evaluates to true if checkbox is checked and submit button is pressed
        receivers = request.POST.getlist("send_requests") 
        # this send_requests object is checkboxes # list of all the checkboxes that we checked
        for receiver in receivers: # go  through each receiver and get their profile so we can create a relationship
            # receivers is a list of ids of profiles
            receiver_profile = Profile.objects.get(id=receiver) 
            Relationship.objects.create(sender=user_profile, receiver=receiver_profile, status='sent')
        return redirect('FeedApp:friends')

    # this is to process all received requests
    if request.method == 'POST' and request.POST.get("receive_requests"):
        senders = request.POST.getlist("receive_requests") # list of senders
        for sender in senders:
            # update the relationship model for the sender to status 'accepted' 
            Relationship.objects.filter(id=sender).update(status='accepted')

            # create a relationship object to access the sender's user id # to add to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user) 
            # the relationship object has a field called user 
            # By saying sender.user, we get the id of the person that sent the request, 
            # # and then adding the user_profile to the friends’ list of the current user.

            # add the user to the friends list of the sender's profile
            relationship_obj.sender.friends.add(request.user)

    context = {'user_friends_profiles': user_friends_profiles, 'user_relationships': user_relationships, 'all_profiles': all_profiles, 'request_received_profiles': request_received_profiles}
    return render(request, 'FeedApp/friends.html', context)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.db.models import Count
from .models import User, Secret, Like
from django.contrib import messages
import datetime
# Create your views here.

#main login/register landing page
def index(request):
    return render(request, 'dojo_app/index.html')

#route when user submits registration form
def register_process(request):
    if request.method == "POST":
        #get registration form user inputs
        postData = {
            'first_name' : request.POST['first_name'],
            'last_name' : request.POST['last_name'],
            'email' : request.POST['email'],
            'password' : request.POST['password'],
            'confirm_password' : request.POST['confirm_password']
        }

        #validate inputs. if valid, create user
        user = User.objects.validate_me(postData)

        #if user was valid & created
        if user[0] == True:
            request.session['login'] = user[1].id
            return redirect('/secrets')
        #if user was invalid & not created
        else:
            errors = user[1]
            for error in errors:
                messages.add_message(request, messages.INFO, error)
            return redirect('/')

#login process
def login(request):
    if request.method == "POST":
        #get login form user inputs
        postData = {
            'email' : request.POST['email'],
            'password' : request.POST['password'],
        }
        #check for matches in stored users
        #if there is a match, login
        user = User.objects.login(postData)
        #if logged in, set session
        if user[0]:
            request.session['login'] = user[1]
            return redirect('/secrets')
        #if not logged in, add error message
        else:
            messages.add_message(request, messages.INFO, 'Invalid login')
            return redirect('/')

#route to secrets page on successful login/registration
def secrets(request):
    #create an array of tuples
    #stores a secret object as first item [0],
    #and a formatted timedelta as the second item [1] in the tuple
    #the third item [2] in the tuple is another tuple:
        #first item [0] is number of likes
        #second item [1] is bool: True if curr user has   liked
        #this secret. False if curr user has not yet liked this secret
    #the fourth item [3] is bool: whether current user posted this
    #(secret-object, timedelta, (num_likes, curr-user-liked), user_wrote)
    secret_info = []
    # get all secrets in order of most recently created first
    secrets = Secret.objects.all().order_by('-created_at')
    for secret in secrets:
        time_change = Secret.objects.find_time_since_posting(secret)
        num_likes = Secret.objects.count_likes_in(secret)
        postData = {
            'user_id' : request.session['login'],
            'secret' : secret
        }
        user_liked = Like.objects.user_has_liked(postData)
        user_wrote = Secret.objects.user_wrote_this(postData)
        secret_info.append((secret, time_change, (num_likes, user_liked), user_wrote))
    #get current logged-in user
    user = User.objects.get(pk=request.session['login'])

    context = {
        'user' : user,
        'secrets' : secret_info,
    }
    return render(request, 'dojo_app/success.html', context)

#post a secret
def post_secret(request):
    if request.method == "POST":
        user_id = User.objects.get(pk=request.session['login'])
        postData = {
            'user_id' : user_id,
            'secret_text' : request.POST.get('secret')
        }

        secret = Secret.objects.post_secret(postData)
        #if secret was added to secret table
        if secret:
            return redirect('/secrets')
        else:
            messages.add_message(request, messages.INFO, "Cannot post empty secret, sorry!")
            return redirect('/secrets')

#like a post
def like(request, id):
    postData = {
        'user_id' : request.session['login'],
        'secret_id' : id
    }
    Like.objects.add_like(postData)
    return redirect('/secrets')

#delete secret
def delete(request, id):
    secret = Secret.objects.get(pk=id)
    secret.delete()
    return redirect('/secrets')

def popular(request):
    #create an array of tuples
    #stores a secret object as first item [0],
    #and a formatted timedelta as the second item [1] in the tuple
    #the third item [2] in the tuple is another tuple:
        #first item [0] is number of likes
        #second item [1] is bool: True if curr user has   liked
        #this secret. False if curr user has not yet liked this secret
    #the fourth item [3] is bool: whether current user posted this
    #(secret-object, timedelta, (num_likes, curr-user-liked), user_wrote)
    secret_info = []
    # get all secrets in order of most recently created first
    secrets = Secret.objects.all().annotate(num_likes=Count('like')).order_by('-num_likes')
    for secret in secrets:
        time_change = Secret.objects.find_time_since_posting(secret)
        num_likes = Secret.objects.count_likes_in(secret)
        postData = {
            'user_id' : request.session['login'],
            'secret' : secret
        }
        user_liked = Like.objects.user_has_liked(postData)
        user_wrote = Secret.objects.user_wrote_this(postData)
        secret_info.append((secret, time_change, (num_likes, user_liked), user_wrote))
    #get current logged-in user
    user = User.objects.get(pk=request.session['login'])

    context = {
        'user' : user,
        'secrets' : secret_info,
    }
    return render(request, 'dojo_app/popular.html', context)
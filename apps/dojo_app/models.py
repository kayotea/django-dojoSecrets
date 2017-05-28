# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import re
import bcrypt
import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
    # def validate_me(self, first_name, last_name, email, password, confirm_password):
    def validate_me(self, postData):
        error = []
        #get info from postData: purely for readability
        f_n = postData['first_name']
        l_n = postData['last_name']
        eml = postData['email']
        pwd = postData['password']
        c_pwd = postData['confirm_password']

        #validations
        if len(f_n) <= 2 or not f_n.isalpha():
            error.append('First name invalid.')
        if len(l_n) <= 2 or not l_n.isalpha():
            error.append('Last name is not valid.')
        if not EMAIL_REGEX.match(eml):
            error.append('Email is invalid')
        if len(pwd) < 8 or pwd != c_pwd:
            error.append('Passwords do not match.')
        #check that given email is not already stored in user table
        users = User.objects.all()
        for user in users:
            if eml == user.email:
                error.append('Email already registered.')
        #if there are no errors with user inputs:
        if len(error) == 0:
            pwd = pwd.encode('utf-8')
            hashed_pwd = bcrypt.hashpw(pwd, bcrypt.gensalt())
            u = User.objects.create(first_name=f_n, last_name=l_n, email=eml, password=hashed_pwd)
            return [True, u]
        #if there are errors with user inputs
        else:
            return [False, error]
    def login(self, postData):
        #get email from postData: just for readability
        eml = postData['email']
        pwd = postData['password']
        pwd = pwd.encode('utf-8')
        #check if there is a match in registered users
        users = User.objects.all()
        for user in users:
            #encode inputted password in preparation for hashing
            user.password = user.password.encode('utf-8')
            #if there is a match, login
            if eml == user.email and bcrypt.hashpw(pwd, user.password) == user.password:
                return [True, user.id]
        #if there is no match, error
        return [False, False]

class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return 'id: '+str(self.id)

#manage those secrets
class SecretManager(models.Manager):
    def post_secret(self, postData):
        usr = postData['user_id']
        msg = postData['secret_text']
        #check that secret is not empty
        if msg == "":
            return False
        #if secret is indeed nto empty, add secret
        else:
            s = Secret.objects.create(user=usr, secret=msg)
            return True
    def delete_secret(self, postData):
        id = postData['secret_id']
        s = Secret.objects.get(pk=id)
        s.delete()
        return
    def find_time_since_posting(self, secret):
        #get timedelta between now and when secret was created
        timedelta = datetime.datetime.now() - secret.created_at.replace(tzinfo=None)
        #get time delta in readable units - hours, minutes, seconds
        days, hours, minutes, seconds = Secret.objects.readable_timedelta(timedelta)

        #if days have passed
        if days > 0:
            display_time = {
                'days' : days
            }
        #if hours have passed
        elif hours > 0:
            display_time = {
                'hours': hours,
                'minutes': minutes,
            }
        #if minutes have passed
        elif minutes > 0:
            display_time = {'minutes': minutes,}
        #if seconds have passed
        else:
            display_time = {'seconds': seconds}
        return display_time

    #make timedelta readable
    def readable_timedelta(self, time):
        days, seconds = time.days, time.seconds
        hours = days*24 + seconds//3600
        minutes = (seconds % 3600)//60
        seconds  =(seconds % 60)
        return days, hours, minutes, seconds

    def count_likes_in(self, secret):
        count = 0
        likes = Like.objects.all()
        for like in likes:
            if like.secret.id == secret.id:
                count += 1
        return count

    def user_wrote_this(self, postData):
        #the user who is currently logged in
        user = User.objects.get(pk=postData['user_id'])
        #the secret in question
        secret = postData['secret']
        #check secrets: if user wrote it, return true
        if secret.user == user:
            return True
        


#class of secrets...
class Secret(models.Model):
    user = models.ForeignKey(User)
    secret = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SecretManager()

    def __str__(self):
        return 'secret id:'+str(self.id)

#manage those likes
class LikeManager(models.Manager):
    def add_like(self, postData):
        #the user who made the like
        user = User.objects.get(pk=postData['user_id'])
        #the secret the like is attached to
        secret = Secret.objects.get(pk=postData['secret_id'])
        #create the Like
        Like.objects.create(user=user, secret=secret)
        return
    def user_has_liked(self, postData):
        user = User.objects.get(pk=postData['user_id'])
        secret = postData['secret']
        likes = Like.objects.all()
        #check all likes: if there is a that contains both
        #given user and given secret
        #return true
        for like in likes:
            if like.user == user and like.secret == secret:
                return True
        else:
            return False

#class of likes
class Like(models.Model):
    user = models.ForeignKey(User)      #which user make this like
    secret = models.ForeignKey(Secret)  #which secret this like is on
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LikeManager()

    def __str__(self):
        return 'like id:'+str(self.id)
from google.appengine.ext import ndb
import webapp2
import jinja2
import hashlib
import random
import urllib
from datetime import timedelta, datetime

class Secret(ndb.Model):
    secret = ndb.StringProperty(indexed=False)
    expired = ndb.DateTimeProperty()

class User(ndb.Model):
    """
    define a google api like interface
    but implement by ourselves to avoid uncertain condition
    """
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    password = ndb.StringProperty(indexed=False)

    secrets = ndb.LocalStructuredProperty(Secret, indexed=False, repeated=True)

    LOGIN_TIMEINTERVAL = timedelta(days=2)

    def nickname(self):
        return self.username

    def email(self):
        return email

    def user_id(self):
        return self.key.id()

    @classmethod
    def get_by_username(self, username):
        return User.query(User.username == username).get()

    def put(self):
        now = datetime.utcnow()
        self.secrets = [k for k in self.secrets if k.expired > now]
        return super(User, self).put()

    def assign_secret(self):
        secret = hashlib.sha1(random.random())
        self.secrets.append(Secret(
            secret=secret,
            expired=datetime.utcnow() + cls.LOGIN_TIMEINTERVAL
        ))
        self.put()
        return secret

    @classmethod
    def login_by_secret(cls, username, secret):
        user = User.get_by_username(username)
        if user and secret and user.auth_secret(secret):
            return user

    @classmethod
    def login(cls, username, password):
        user = User.get_by_username(username)
        if user and password and user.auth(password):
            return user

    def auth(self, password):
        return self.password == hashlib.sha1(password).hexdigest()

    def auth_secret(self, secret):
        now = datetime.utcnow()
        return secret in [k.secret for k in user.secrets if k.expired > now]

    @classmethod
    def register(cls, username, password):
        user = User.get_by_username(username)
        assert not user # username is in used

        user = User(
            username=username,
            password=password
        )
        user.put()
        return user


def get_current_user(handler):
    username = handler.request.cookies.get('uid')
    secret = handler.request.cookies.get('secret')

    if not username or not secret: return
    return User.login_by_secret(username, secret)

def login_required(handler_method):
    def wrap(self, *args):
        user = get_current_user(self)
        if not user:
            return self.redirect(create_login_url(self.request.uri))
        return handler_method(self, *args)
    return wrap

def create_login_url(uri):
    return '/user/login?redirect=' + urllib.urlencode(uri)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        redirect = self.request.get('redirect_uri')
        template = jinja2.Template(open('templates/login.html').read())
        self.response.out.write(
            template.render({'redirect_uri': redirect})
        )

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        redirect = self.request.get('redirect_uri')

        user = User.login(username, password)
        if not user:
            return self.response.out.write(False)

        self.response.set_cookie("uid", user.username)
        self.response.set_cookie("secret", user.gen_secret())

        if redirect:
            return self.redirect(redirect)

        self.response.out.write(True)

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        user = get_current_user(self)
        if user:
            self.response.delete_cookie("uid")
            self.response.delete_cookie("secret")

app = webapp2.WSGIApplication([
    (r'/user/login', LoginHandler),
    (r'/user/logout', LogoutHandler)
], debug=False)

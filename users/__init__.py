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
    email = ndb.StringProperty()
    password = ndb.StringProperty(indexed=False)

    secrets = ndb.LocalStructuredProperty(Secret, indexed=False, repeated=True)

    LOGIN_TIMEINTERVAL = timedelta(days=2)

    def nickname(self):
        return self.email

    # def email(self):
    #     return self.email

    def user_id(self):
        return self.key.id()

    @classmethod
    def get_by_email(self, email):
        return User.query(User.email == email).get()

    def put(self):
        now = datetime.utcnow()
        self.secrets = [k for k in self.secrets if k.expired > now]
        return super(User, self).put()

    def assign_secret(self):
        secret = hashlib.sha1(str(random.random())).hexdigest()
        self.secrets.append(Secret(
            secret=secret,
            expired=datetime.utcnow() + self.LOGIN_TIMEINTERVAL
        ))
        self.put()
        return secret

    @classmethod
    def login_by_secret(cls, email, secret):
        user = User.get_by_email(email)
        if user and secret and user.auth_secret(secret):
            return user

    @classmethod
    def login(cls, email, password):
        user = User.get_by_email(email)
        if user and password and user.auth(password):
            return user

    def auth(self, password):
        return self.password == hashlib.sha1(password).hexdigest()

    def auth_secret(self, secret):
        now = datetime.utcnow()
        return secret in [k.secret for k in user.secrets if k.expired > now]

    @classmethod
    def register(cls, email, password):
        user = User.get_by_email(email)
        if user: return
        # assert not user # username is in used

        user = User(
            email=email,
            password=hashlib.sha1(password).hexdigest()
        )
        user.put()
        return user


def get_current_user(handler):
    email = handler.request.cookies.get('uid')
    secret = handler.request.cookies.get('secret')

    if not email or not secret: return
    return User.login_by_secret(email, secret)

def login_required(handler_method):
    def wrap(self, *args):
        user = get_current_user(self)
        if not user:
            return self.redirect(create_login_url(self.request.uri))
        return handler_method(self, *args)
    return wrap

def create_login_url(uri):
    return '/user/login?redirect_uri=' + urllib.quote(uri)

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        redirect = self.request.get('redirect_uri')
        template = jinja2.Template(open('templates/login.html').read())
        self.response.out.write(
            template.render({'redirect_uri': redirect})
        )

    def post(self):
        email = self.request.get('email')
        password = self.request.get('password')
        redirect = self.request.get('redirect_uri')

        user = User.login(email, password)
        if not user:
            return self.response.out.write(False)

        self.response.set_cookie("uid", str(user.email))
        self.response.set_cookie("secret", str(user.assign_secret()))

        if redirect:
            return self.redirect(str(redirect))

        self.response.out.write(True)

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        user = get_current_user(self)
        if user:
            self.response.delete_cookie("uid")
            self.response.delete_cookie("secret")

class RegisterHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja2.Template(open('templates/register.html').read())
        self.response.out.write(
            template.render({})
        )

    def post(self):
        password = self.request.get("password")
        email = self.request.get("email")

        user = User.register(email, password)
        if user:
            return self.response.out.write(True)

        self.response.out.write(False)

app = webapp2.WSGIApplication([
    (r'/user/login', LoginHandler),
    (r'/user/logout', LogoutHandler),
    (r'/user/register', RegisterHandler),
], debug=False)

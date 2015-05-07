# -*- encoding=utf8 -*-

import logging
import unittest
from google.appengine.ext import testbed
from users import *
import webtest
import urllib


class UserTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_all_stubs()
        self.testapp = webtest.TestApp(app)
        User.register("old@tagtoo.org", "passwd")

        return

    def tearDown(self):
        self.testbed.deactivate()
        return


    def test_register_get(self):
        response = self.testapp.get("/user/register")
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        response = self.testapp.post("/user/register", {"email": "new@tagtoo.org", "password": "passwd"})
        self.assertEqual(response.body, "True")
        self.assertEqual(2, len(User.query().fetch(5)))

    def test_register_post_fail(self):
        response = self.testapp.post("/user/register", {"email": "old@tagtoo.org", "password": "passwd"})
        self.assertEqual(response.body, "False")
        self.assertEqual(1, len(User.query().fetch(5)))

    def test_login_get(self):
        redirect_uri = urllib.quote("http://example.com")
        response = self.testapp.get("/user/login", {"redirect_uri": redirect_uri})
        hidden_value = response.html.select("input[name=redirect_uri]")[0].attrs.get("value")
        self.assertEqual(hidden_value, redirect_uri)

    def test_login_post_success(self):
        response = self.testapp.post("/user/login", {"email": "old@tagtoo.org", "password": "passwd"})
        self.assertEqual(response.body, "True")
        self.assertIsNotNone(self.testapp.cookies["uid"])
        self.assertIsNotNone(self.testapp.cookies["secret"])

    def test_login_post_fail(self):
        response = self.testapp.post("/user/login", {"email": "new@tagtoo.org", "password": "passwd"})
        self.assertEqual(response.body, "False")
        self.assertNotIn("uid", self.testapp.cookies)
        self.assertNotIn("secret", self.testapp.cookies)

    def test_logout(self):
        # simply login, the unit test for login is in test_login_success function
        response = self.testapp.post("/user/login", {"email": "old@tagtoo.org", "password": "passwd"})
        response = self.testapp.get("/user/logout")
        self.assertNotIn("uid", self.testapp.cookies)
        self.assertNotIn("secret", self.testapp.cookies)


if __name__ == '__main__':
    unittest.main()

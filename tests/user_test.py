# -*- encoding=utf8 -*-

import unittest
from google.appengine.ext import testbed
from users import *
import webtest


class UserTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_all_stubs()

        self.cookies = {}
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

    def test_register_post_fail(self):
        response = self.testapp.post("/user/register", {"email": "old@tagtoo.org", "password": "passwd"})
        self.assertEqual(response.body, "False")


if __name__ == '__main__':
    unittest.main()

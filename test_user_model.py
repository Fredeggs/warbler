"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from psycopg2 import IntegrityError

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test models for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        # User should have a repr method that displays the username and email
        self.assertIn("testuser, test@test.com>", str(u.__repr__))

    def test_is_following(self):
        """Does the is_following method work?"""

        u1 = User(
            email="test1@test.com", username="testuser1", password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD"
        )

        user_data = [u1, u2]
        db.session.add_all(user_data)
        db.session.commit()

        follow = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(follow)
        db.session.commit()

        # User1 should be shown as following User2
        self.assertEqual(u1.is_following(u2), True)
        # User2 should be shown as NOT following User1
        self.assertEqual(u2.is_following(u1), False)

    def test_is_followed_by(self):
        """Does the is_followed_by method work?"""

        u1 = User(
            email="test1@test.com", username="testuser1", password="HASHED_PASSWORD"
        )
        u2 = User(
            email="test2@test.com", username="testuser2", password="HASHED_PASSWORD"
        )

        user_data = [u1, u2]
        db.session.add_all(user_data)
        db.session.commit()

        follow = Follows(user_being_followed_id=u2.id, user_following_id=u1.id)
        db.session.add(follow)
        db.session.commit()

        # User2 should be shown as being followed by User1
        self.assertEqual(u2.is_followed_by(u1), True)
        # User1 should be as NOT being followed by User2
        self.assertEqual(u1.is_followed_by(u2), False)

    def test_signup_user(self):
        """Does the User.signup method work?"""

        u_test = User.signup("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_user_authenticate(self):
        """Does the User.authenticate method work?"""

        u_1 = User.signup("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_1.id = uid
        db.session.commit()

        u_test = User.query.get(uid)

        # User.authenticate successfully returns a user when given a valid username and password
        self.assertEqual(User.authenticate("testtesttest", "password"), u_test)

        # User.authenticate returns False when given invalid username and/or password
        self.assertEqual(User.authenticate("incorrectusername", "password"), False)
        self.assertEqual(User.authenticate("testtesttest", "incorrectpassword"), False)

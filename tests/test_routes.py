"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    def test_list_all_accounts(self):
        """It should list all the accounts"""
        account1 = AccountFactory()
        account2 = AccountFactory()
        self.client.post(BASE_URL, json=account1.serialize())
        self.client.post(BASE_URL, json=account2.serialize())

        # Make a GET request to the /accounts endpoint
        response = self.client.get(BASE_URL)

        # Check the response status and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)  # We created 2 accounts
        self.assertEqual(data[0]["name"], account1.name)
        self.assertEqual(data[1]["name"], account2.name)

    def test_list_accounts_empty(self):
        """It should return an empty list when no accounts exist"""
        # Ensure no accounts exist
        response = self.client.get(BASE_URL)

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data, [])  # Should return an empty list

    def test_read_account(self):
        """It should read an account by its ID"""
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Extract the created account's ID
        account_id = response.get_json()["id"]

        response = self.client.get(f"{BASE_URL}/{account_id}")  # Make a GET request to fetch by ID
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["id"], account_id)
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
        self.assertEqual(data["address"], account.address)
        self.assertEqual(data["phone_number"], account.phone_number)
        self.assertEqual(data["date_joined"], str(account.date_joined))

    def test_update_account(self):
        """It should update an account by its ID"""
        # Step 1: Create a test account
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 2: Extract account ID and prepare updated data
        new_account = response.get_json() # extract JSON response
        account_id = new_account["id"]
        updated_data = {
            "name": "Updated Name",
            "email": "updated_email@example.com",
            "address": "Updated Address",
            "phone_number": "1234567890",
            "date_joined": new_account["date_joined"],  # Keep original date
        }

        # Step 3: Send PUT request to update the account
        update_response = self.client.put(f"{BASE_URL}/{account_id}", json=updated_data)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK) #verify success

        updated_account = update_response.get_json()
        self.assertEqual(updated_account["name"], updated_data["name"])
        self.assertEqual(updated_account["email"], updated_data["email"])
        self.assertEqual(updated_account["address"], updated_data["address"])
        self.assertEqual(updated_account["phone_number"], updated_data["phone_number"])
        self.assertEqual(updated_account["date_joined"], updated_data["date_joined"])

        # Step 5: Test 404 Not Found for non-existent account
        invalid_id = 99999  # Non-existent ID
        response = self.client.put(f"{BASE_URL}/{invalid_id}", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_account(self):
        """Deleting an account by its ID"""
        # Step 1 Create account
        account = AccountFactory()
        response = self.client.post(BASE_URL, json=account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Extract the account ID
        new_account = response.get_json()  # extract JSON response
        account_id = new_account["id"]

        # Send DELETE request
        delete_response = self.client.delete(f"{BASE_URL}/{account_id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the account is deleted
        get_response = self.client.get(f"{BASE_URL}/{account_id}")
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

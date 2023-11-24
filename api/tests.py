from django.test import TestCase, Client
from api.ledger import LedgerClient
from unittest.mock import patch, MagicMock
import django
django.setup()


class TestLedgerClientProcess(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.auth_code = None

    def test_ledger_process(self):
        # Mock the authorization URL returned by _get_connection
        with patch.object(LedgerClient, '_get_connection', return_value=f'/accounts/quickbooks/login/callback//?code={self.auth_code}&realmId=test_realm_id'):
            # Simulate the request to initiate the QuickBooks connection
            response = self.client.get('/initiate_ledger_process/')
            self.assertEqual(response.status_code, 302)  # Expecting a redirect

            # Assuming your view sets a session variable 'qbo_auth_code'
            auth_code = response.client.session.get('qbo_auth_code')

            # Mock the initiate_quick_book method to avoid actual API calls
            with patch.object(LedgerClient, 'initiate_quick_book', MagicMock()):
                # Simulate the callback from QuickBooks with the mocked auth_code and realm_id
                callback_response = self.client.get(f'/accounts/quickbooks/login/callback//?code={auth_code}&realmId=test_realm_id')
                self.assertEqual(callback_response.status_code, 200)  # Assuming successful callback

                # Now you can assert the expected behavior based on the mocked LedgerClient methods
                # For example, you can check if your data retrieval methods are called as expected
                # You may also mock the actual API calls made by LedgerClient for more fine-grained control

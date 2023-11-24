from decouple import config
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from quickbooks import QuickBooks
from quickbooks.objects.bill import Bill
from quickbooks.objects.vendor import Vendor


class LedgerClientBase:
    """Base Ledger Integration Client class"""

    def __init__(self):
        self._connection = self._get_connection()

    def _get_connection(self):
        raise NotImplementedError("`_get_connection()` must be implemented.")

    def get_bills(self, num=50, vendor_id=None):
        raise NotImplementedError("`get_bills()` must be implemented.")

    def get_bill(self, bill_id):
        raise NotImplementedError("`get_bill()` must be implemented.")

    def get_vendors(self, num=50):
        raise NotImplementedError("`get_vendors()` must be implemented.")

    def get_vendor(self, vendor_id):
        raise NotImplementedError("`get_vendor()` must be implemented.")


class LedgerClient(LedgerClientBase):
    def __init__(self, bill_id=1, vendor_id=56):
        self.client_id = config("QBOOK_CLIENT_ID", None)
        self.client_secret = config("QBOOK_CLIENT_SECRET", None)
        self.environment = config("QBOOK_ENVIRONMENT", None)
        self.redirect_uri = config("QBOOK_REDIRECT_URI", None)
        self.company_id = config("QBOOK_COMPANY_ID", None)

        self.client = None
        self.bill_id = bill_id
        self.vendor_id = vendor_id
        self.single_bill_data = None
        self.single_vendor_data = None
        self.list_bills = []
        self.list_vendors = []

        self._setup_quickbooks_client()
        super().__init__()

    def _setup_quickbooks_client(self):
        # Use client credentials to get the access token
        client = BackendApplicationClient(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        token_url = f"https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        token = oauth.fetch_token(
            token_url=token_url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
        )

        # Initialize QuickBooks client
        self.client = QuickBooks(
            auth_client=None,  # No need for auth client since we have the token
            access_token=token['access_token'],
            company_id=self.company_id,
            minorversion=1
        )

    def get_bills(self, num=50, vendor_id=None):
        try:
            all_bills = Bill.all(qb=self.client, max_results=50)
            for bill in all_bills:
                bill_data = {"id": bill.Id, "balance": bill.Balance, "vendor_name": bill.VendorRef.name}
                self.list_bills.append(bill_data)
        except Exception as e:
            print(f"Error getting bills: {e}")

    def get_bill(self, bill_id):
        try:
            single_bill = Bill.get(qb=self.client, id=self.bill_id)
            self.single_bill_data = single_bill
        except Exception as e:
            print(f"Error getting bill: {e}")

    def get_vendors(self, num=50):
        try:
            all_vendors = Vendor.all(qb=self.client, max_results=50)
            for vendor in all_vendors:
                vendor_data = {"id": vendor.Id, "balance": vendor.Balance, "vendor_name": vendor.DisplayName}
                self.list_vendors.append(vendor_data)
        except Exception as e:
            print(f"Error getting vendors: {e}")

    def get_vendor(self, vendor_id):
        try:
            single_vendor = Vendor.get(qb=self.client, id=self.vendor_id)
            self.single_vendor_data = single_vendor
        except Exception as e:
            print(f"Error getting vendor: {e}")

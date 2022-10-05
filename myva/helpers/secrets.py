import json
from google.cloud import secretmanager


class Names:

    TWILIO = "projects/150895630238/secrets/TWILIO"
    MAPS_API_KEY = "projects/150895630238/secrets/GOOGLE_MAPS_API_KEY"


class MyVA411Secrets:

    def __init__(self, project=None):
        self.client = secretmanager.SecretManagerServiceClient()
        self.manager = secretmanager
        self.twilio = json.loads(self.access_secret(Names.TWILIO))
        self.twilio_account_sid = self.twilio.get("ACCOUNT_SID")
        self.twilio_account_auth_token = self.twilio.get("AUTH_TOKEN")
        self.twilio_phone_number = self.twilio.get("PHONE_NUMBER")
        self.maps_api_key = self.access_secret(Names.MAPS_API_KEY)

    def access_secret(self, name):
        request = self.manager.AccessSecretVersionRequest(name=name)
        response = self.client.access_secret_version(request)
        data = response.payload.data
        return data.decode()

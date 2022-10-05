from google.cloud import secretmanager


class Names:

    TWILIO_ACCOUNT_SID = "projects/holy-diver-297719/"\
        "secrets/TWILIO_ACCOUNT_SID/"\
        "versions/latest"
    TWILIO_AUTH_TOKEN = "projects/holy-diver-297719/"\
        "secrets/TWILIO_AUTH_TOKEN/"\
        "versions/latest"
    MAPS_API_KEY = "projects/holy-diver-297719/"\
        "secrets/MAPS_API_KEY/"\
        "versions/latest"


class MyVA411Secrets:

    def __init__(self, project=None):
        self.client = secretmanager.SecretManagerServiceClient()
        self.manager = secretmanager
        self.twilio_account_sid = self.access_secret(Names.TWILIO_ACCOUNT_SID)
        self.twilio_auth_token = self.access_secret(Names.TWILIO_AUTH_TOKEN)
        self.maps_api_key = self.access_secret(Names.MAPS_API_KEY)

    def access_secret(self, name):
        request = self.manager.AccessSecretVersionRequest(name=name)
        response = self.client.access_secret_version(request)
        data = response.payload.data
        return data.decode()

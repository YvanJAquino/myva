import os
from urllib.parse import urlunparse, urlencode
from typing import Callable

from fastapi import FastAPI
from twilio.rest import Client

from cxwebhooks import WebhookRequest, WebhookResponse

from helpers.secrets import MyVA411Secrets
from helpers.maps import find_nearest_facilities

app = FastAPI()
secrets = MyVA411Secrets()
sms = Client(secrets.twilio_account_sid, secrets.twilio_auth_token)

TWILIO_PHONE_NUMBER = secrets.twilio_phone_number


def make_maps_url(address: str) -> str:
    # https://www.google.com/maps/dir/?api=1&parameters
    parameters = {
        'api': 1,
        'destination': address,
        'travelmode': 'driving'
    }
    scheme = 'https'
    netloc = 'www.google.com'
    path = '/maps/dir/'
    query = urlencode(parameters)
    return urlunparse((scheme, netloc, path, None, query, None))


def staging(path_fn: Callable) -> Callable:
    async def call(
        webhook: WebhookRequest,
        response=None,
        caller_id=None,
        session_params=None,
        session_id=None
    ):
        response = WebhookResponse()
        caller_id = webhook.payload.get('telephony', {}).get('caller_id')
        session = webhook.sessionInfo
        return await path_fn(
            webhook,
            response=response,
            caller_id=caller_id,
            session_params=session.parameters,
            session_id=session.session
        )
    return call


@app.post("/find_nearest")
@staging
async def find_nearest_location(
    webhook: WebhookRequest,
    response=...,
    caller_id=...,
    session_params=...,
    session_id=...
):
    zip_code = session_params.get('zip_code')
    if zip_code:
        locations = find_nearest_facilities(zip_code, secrets.maps_api_key)
        address = locations[0]['address']
        response.add_text_response(
            f"Please give me a moment while I locate the nearest VA medical"
            f"center.\nThe nearest "
            f"medical center to {' '.join(str(zip_code))} is {address}."
            f"Would you like me to send this information to you "
            f"via text message?"
        )
        response.add_audio_text_response(
            f'Please give me a moment while I locate the nearest VA medical'
            f' center.  The nearest medical center to '
            f'<say-as interpret-as="verbatim">{" ".join(str(zip_code))}'
            f'</say-as> is {address}. Would you like me to send this'
            f'information to you via text message?'
        )
        response.add_payload({'locations': locations, 'locations_index': 0})
    else:
        response.add_text_response(
            "Uh oh, something went wrong!  Check the logs.")
    return response


@app.post('/text_nearest_address')
@staging
async def send_text_address(
    webhook: WebhookRequest,
    response=...,
    caller_id=...,
    session_params=...,
    session_id=...
):
    phone_number = session_params.get('phone_number')
    locations = session_params.get('locations')
    locations_index = session_params.get('locations_index')
    addr = locations[locations_index]['address']
    addr_map_url = make_maps_url(addr)
    body = f"Your preferred VA Medical Center is {addr}"
    body_dir = f"Here's a link with directions: {addr_map_url}"
    sms.messages.create(
        body=body,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    sms.messages.create(
        body=body_dir,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

    fmtd_phone_num = (
        f'({phone_number[:3]}) '
        f'{phone_number[3:6]}-'
        f'{phone_number[6:]}'
    )
    response.add_text_response(
        f"No problem, we've sent a text message to {fmtd_phone_num}"
    )
    response.add_audio_text_response(
        f"No problem, we've sent a text message to {fmtd_phone_num}"
    )
    return response

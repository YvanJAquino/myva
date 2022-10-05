import googlemaps

from helpers.data import DESTINATIONS


def find_nearest_facilities(address: str, API_KEY: str) -> list:
    gmaps = googlemaps.Client(key=API_KEY)
    distance_matrix = gmaps.distance_matrix(
        origins=address,
        destinations=DESTINATIONS,
        mode='driving')
    sorted_matrix = [(
            distance_matrix['destination_addresses'][idx],
            distance_matrix['rows'][0]['elements'][idx]['distance']['value'],
            distance_matrix['rows'][0]['elements'][idx]['duration']['value']
        ) for idx in range(len(DESTINATIONS))]
    sorted_matrix.sort(key=lambda r: r[2])
    return [
        {
            'address': sm[0],
            'distance': sm[1],
            'duration': sm[2]
        } for sm in sorted_matrix
    ]

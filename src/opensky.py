import json
import requests

from opensky_api import OpenSkyApi, StateVector

config = None
with open( "data/opensky.json" ) as fp:
    config = json.load( fp )

api = OpenSkyApi(
    config["auth"]["username"],
    config["auth"]["password"]
)

def get_states( *args, **kwargs ):
    return( api.get_states( **kwargs ) )


def get_flights( icao24=None, begin=None, end=None ):
    
    req = requests.get(
        "https://opensky-network.org/api/flights/aircraft",
        params={
            "icao24" : icao24,
            "begin" : begin,
            "end" : end
        }
    )

    if req.status_code == 200:
        return req.json()

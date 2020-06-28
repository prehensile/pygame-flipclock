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


def get_route( callsign ):
    req = requests.get(
        "https://opensky-network.org/api/routes",
        params={
            "callsign" : callsign,
        }
    )

    if req.status_code == 200:
        return req.json()
    else:
        print( req )
        print( req.status_code )
        print( req.text )


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
    else:
        print( req )
        print( req.status_code )
        print( req.text )


if __name__ == "__main__":
    import time
    ts = int( time.time() )
    print(
        get_flights(
            icao24 = "BCS395",
            begin = ts - (60*60*24),
            end = ts
        )
    )

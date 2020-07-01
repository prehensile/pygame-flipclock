import json

import requests
from sources.opensky_api import OpenSkyApi, StateVector

from model import Airport, Flight
from sources import utils


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
        raise Exception( req.status_code )


def parse_flights( j ):
    return utils.parse_flights(
        j, "estDepartureAirport", "estArrivalAirport"
    )
    # return map(
    #     lambda f: Flight(
    #         Airport( f["estDepartureAirport"] ),
    #         Airport( f["estArrivalAirport"] )
    #     ),
    #     j
    # )


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
        j = req.json()
        return parse_flights( j )
    else:
        # print( req )
        # print( req.status_code )
        # print( req.text )
        raise Exception( req.text )


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

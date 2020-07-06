import json
import sys
import logging
import os

import requests

from ..model import Airport, Flight
from ..sources import utils


config = None
pth_config = os.path.join(
    os.path.dirname(__file__),
    "../data/aviationstack.json"
)
with open( pth_config ) as fp:   
    config = json.load( fp )

root_url = "http://api.aviationstack.com/v1/"


def make_request( endpoint, params={} ):
    url = "{}{}".format( root_url, endpoint )
    params["access_key"] = config["api_key"]
    r = requests.get( url, params )
    logging.debug( r.text )
    return r.json()["data"]


def parse_flights( j ):
    # return map(
    #     lambda f: Flight(
    #         Airport( f['departure']['icao'] ),
    #         Airport( f['arrival']['icao'] )
    #     ),
    #     j
    # )
    return utils.parse_flights(
        j, "departure.icao", "arrival.icao"
    )


def get_flights( icao=None ):
    j = make_request(
        "flights",
        {
            "flight_icao" : icao
        }
    )
    return parse_flights(j)


if __name__ == "__main__":
    icao = sys.argv[1]
    flights = get_flights( icao )
    print( flights )
    for f in flights:
        print(f)
        print("***")
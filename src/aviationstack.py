import requests
import json
import sys

config = None
with open( "data/aviationstack.json" ) as fp:   
    config = json.load( fp )

root_url = "http://api.aviationstack.com/v1/"


def make_request( endpoint, params={} ):

    url = "{}{}".format( root_url, endpoint )

    params["access_key"] = config["api_key"]

    r = requests.get( url, params )

    # print( r.text )

    return r.json()["data"]


def get_flights( icao=None ):
    return make_request(
        "flights",
        {
            "flight_icao" : icao
        }
    )

if __name__ == "__main__":
    icao = sys.argv[1]
    flights = get_flights( icao )
    print( flights )
    for f in flights:
        print(f)
        print("***")
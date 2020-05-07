import json
import logging
import re
import sys

import requests

config = None
with open( 'data/flightaware.json' ) as fp:
    config = json.load( fp )

fxml_root = "https://flightxml.flightaware.com/json/FlightXML2/"
fxml_auth = ( config["username"], config["api_key"] )

def request( endpoint, payload ):
    
    response = requests.get(
        fxml_root + endpoint,
        params=payload,
        auth=fxml_auth
    )

    if response.status_code == 200:
        return response.json()
    else:
        print( "Error executing request" )


def flight_info( ident, how_many=1 ):
    payload = { "ident" : ident, "howMany" : how_many }
    req = request( 'FlightInfo', payload )
    if "error" in req:
        raise Exception( req["error"] )
    return( req['FlightInfoResult']['flights'] )


def search( query, how_many=1 ):
    payload = { "query" : query, "howMany" : how_many }
    req = request( 'Search', payload )
    if "error" in req:
        raise Exception( req["error"] )
    return( req )


def scrape_flight_info( ident ):
    # scrape flight info from flightaware's website
    # bit naughty, but it catches more flights than the FlightInfo endpoint does
    # use it as a fallback
    url = "https://flightaware.com/live/flight/" + ident.upper()
    r = requests.get( url )
    # search through page source for bootstrap data
    m = re.search( "var trackpollBootstrap = (.*);</script>", r.text )
    # parse it
    j = json.loads( m.group(1) )
    f = j["flights"]
    # get key for first flight in data object
    k = next(iter(f))
    # retrieve data for first flight
    this_flight = f[k] 
    # data is the object we'll return, with the same keys as flight_info result
    data = {}
    if this_flight["origin"]:
        data[ "origin" ] = this_flight[ "origin" ][ "icao" ]
    if this_flight["destination"]:
        data[ "destination" ] = this_flight[ "destination" ][ "icao" ] 
    if this_flight["ident"]:
        data[ "ident" ] = this_flight[ "ident" ]
    return data


def combined_flight_info( ident ):
    info = None
    try:
        info = flight_info( ident )
    except Exception as e:
        logging.exception( e )
    
    if info is None:
        try:
            info = scrape_flight_info( ident )
        except Exception as e:
            logging.exception( e )

    return info


if __name__ == "__main__":
    # payload = {'airport':'KSFO', 'howMany':'10'}
    # print( request( "Enroute", payload ) )
    icao = sys.argv[1]
    print( combined_flight_info(icao) )

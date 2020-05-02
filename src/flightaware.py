import requests
import json
import sys

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

if __name__ == "__main__":
    # payload = {'airport':'KSFO', 'howMany':'10'}
    # print( request( "Enroute", payload ) )
    icao = sys.argv[1]
    try:
        print( flight_info(icao,2) )
    except Exception as e:
        query = "-identOrReg {}*".format(icao)
        print( search(query) )


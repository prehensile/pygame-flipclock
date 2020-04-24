import requests
import json

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


if __name__ == "__main__":
    # payload = {'airport':'KSFO', 'howMany':'10'}
    # print( request( "Enroute", payload ) )
    print( flight_info('DLH3HT') )


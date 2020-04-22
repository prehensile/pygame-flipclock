from opensky_api import OpenSkyApi, StateVector
import requests
import time
import json
import sqlite3
import random


opensky_data = None
with open( "data/opensky.json" ) as fp:
    opensky_data = json.load( fp )

opensky = OpenSkyApi(
    opensky_data["auth"]["username"],
    opensky_data["auth"]["password"]
)

conn = sqlite3.connect( "data/airports.sqlite")
cur = conn.cursor()

flight_window = 60 * 60 * 24
bbox = tuple( opensky_data["bbox"] )


def airport_for_icao( icao ):
    cur.execute( 'SELECT * FROM airports WHERE icao=?', (icao,) )
    return cur.fetchone()

def format_airport( airport ):
    return "{} ({},{})".format(
        airport[1],
        airport[2],
        airport[3]
    )

def formatted_airport_for_icao( icao ): 
    return format_airport( airport_for_icao(icao) )

def print_flight( j ):

    dep_icao = j["estDepartureAirport"]
    arr_icao = j["estArrivalAirport"]

    dep_airport = None
    arr_airport = None

    if( dep_icao ):
        dep_airport = formatted_airport_for_icao( dep_icao )
    
    if( arr_icao ):
        arr_airport = formatted_airport_for_icao( arr_icao )
    
    display_line = "{} from {} to {}".format(
        j["callsign"].strip(),
        dep_airport,
        arr_airport   
    )

    print( display_line )


while True:

    # 51.448834, -0.140049
    # 51.400140, 0.015570
    # https://opensky-network.org/api/states/all?lamin=51.400140&lomin=-0.140049&lamax=51.448834&lomax=0.015570
    # r = opensky.get_states(bbox=(51.400140, 51.448834, -0.140049, 0.015570))
    # r = opensky.get_states()

    try:

        r = opensky.get_states( bbox=bbox )
    
        if (r is not None) and r.states:
            print( r.states )
            for state in r.states: 
                state_time = state.time_position
                if state_time:
                    req = requests.get(
                        "https://opensky-network.org/api/flights/aircraft",
                        params={
                            "icao24" : state.icao24,
                            "begin" : state_time - flight_window,
                            "end" : state_time + flight_window
                        }
                    )
                
                    if req.status_code == 200:
                        j = req.json()
                
                        for flight in j:
                            print_flight( flight )
    
    except Exception as e:
        print( repr(e) )

    time.sleep( 30.0 )  
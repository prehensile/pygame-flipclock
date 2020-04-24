import requests
import time
import json
import datetime

import random

import airports
import flightaware
import opensky


flight_window = 60 * 60 * 24

def print_flight( dep_icao=None, arr_icao=None, callsign=None  ):

    

    dep_airport = None
    arr_airport = None

    if( dep_icao ):
        dep_airport = airports.formatted_airport_for_icao( dep_icao )
    
    if( arr_icao ):
        arr_airport = airports.formatted_airport_for_icao( arr_icao )
    
    display_line = "{}: {} from {} to {}".format(
        datetime.datetime.now(),
        callsign.strip(),
        dep_airport,
        arr_airport   
    )

    print( display_line )


def print_opensky_flight( j ):
    print_flight(
        dep_icao = j["estDepartureAirport"],
        arr_icao = j["estArrivalAirport"],
        callsign = j["callsign"]
    )


def print_flightaware_flight( f ):
    print_flight(
        dep_icao = f['origin'],
        arr_icao = f['destination'],
        callsign = f['ident']
    )

bbox = tuple( opensky.config["bbox"] )

while True:

    # 51.448834, -0.140049
    # 51.400140, 0.015570
    # https://opensky-network.org/api/states/all?lamin=51.400140&lomin=-0.140049&lamax=51.448834&lomax=0.015570
    # r = opensky.get_states(bbox=(51.400140, 51.448834, -0.140049, 0.015570))
    # r = opensky.get_states()

    try:

        r = opensky.get_states( bbox=bbox )
    
        if (r is not None) and r.states:
            
            for state in r.states: 

                print( "{}: Found a flight with callsign {}".format(
                    datetime.datetime.now(),
                    state.callsign
                ))

                state_time = state.time_position
                
                if state_time:
                    
                    flights = None
                    icao24 = state.icao24,
                    
                    # first, attempt to get flight info from opensky
                    try:
                        flights = opensky.get_flights(
                            icao24 = icao24,
                            begin = state_time - flight_window,
                            end = state_time + flight_window
                        )
                        for flight in flights:
                            print_opensky_flight( flight )
                    except Exception as e:
                        pass
                    
                    # if that fails, try flightaware
                    if flights is None or len(flights) < 1:
                        flights = flightaware.flight_info( icao24 )
                        for flight in flights:
                            print_flightaware_flight( flight )
                        
    
    except Exception as e:
        # print( repr(e) )
        pass

    time.sleep( 30.0 )  
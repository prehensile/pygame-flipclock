import requests
import time
import json
import datetime
import logging
import random
from collections import defaultdict

import airports
import flightaware
import opensky
import airportinfo
import aviationstack
import flightradar24

from model import Airport, Flight


flight_window = 60 * 60 * 24

def format_flight( dep_icao=None, arr_icao=None, callsign=None  ):

    dep_airport = None
    arr_airport = None

    if( dep_icao ):
        dep_airport = airports.formatted_airport_for_icao( dep_icao )
    
    if( arr_icao ):
        arr_airport = airports.formatted_airport_for_icao( arr_icao )
    
    return "{}: {} from {} to {}".format(
        datetime.datetime.now(),
        callsign.strip(),
        dep_airport,
        arr_airport   
    )



def whittle_flights( flights ):
    for flight in flights:
        o = flight.origin
        d = flight.destintion
        if (d is not None) and (o is not None) and (len(o) > 0) and (len(d)>0):
            return flight


def flight_info_flightradar24( callsign ):
    flights = flightradar24.flight_info( callsign )
    f = flights[0]
    return format_flight(
        dep_icao = f.origin,
        arr_icao = f.destination,
        callsign = callsign
    )


success_counts = defaultdict(1)

def get_flight_info( icao24=None, callsign=None, timestamp=None ):
    
    if timestamp is None:
        timestamp = int( time.time() )
                    
    # first, attempt to get route info from opensky
    try:
        print( "Attempt to get flight info from opensky")
        r = opensky.get_route( callsign )
        route = r["route"]
        flights = [
            Flight( 
                Airport( route[0] ),
                Airport( route[-1] )
            )
        ]
        success_counts[ "opensky-routes" ] += 1
        return flights
    except Exception as e:
        print( "opensky.get_route failed: {}".format(
            repr(e)
        ))
    

    # if that fails, attempt to get flight info from opensky
    try:
        print( "Attempt to get flight info from opensky")
            flights = opensky.get_flights(
                icao24 = icao24,
                begin = timestamp - flight_window,
                end = timestamp + flight_window
            )
            if len( flights ) > 0: 
                success_counts[ "opensky-flights" ] += 1
                # opensky flights have the newest at the end of the list
                return reversed( flights )
    except Exception as e:
        print( "opensky.get_flights failed: {}".format(
            repr(e)
        ))


    # if that fails, try flightaware
    try:
        print( "fallback to flightaware")
        flights = flightaware.flight_info( callsign, how_many=3 )
        if len( flights ) > 0:
            success_counts[ "flightaware" ] += 1
            # flightaware flights have the newest at the end of the list
            return reversed( flights )
    except Exception as e:
        print( "flightaware.flight_info failed: {}".format(
            repr(e)
        ))
    
    try:
        print( "fallback to aviationstack")
        flights = aviationstack.get_flights( icao24 )
        if len( flights ) > 1:
            success_counts[ "aviationstack" ] += 1
            return flights
    except Exception as e:
        print( "flight_info_aviationstack failed: {}".format(
            repr(e)
        ))
    
    try:
        print( "fallback to flightradar24")
        flights = flightradar24.flight_info( callsign )
        if len( flights ) > 1:
            return flights
    except Exception as e:
        print( "flight_info_flightradar24 failed: {}".format(
            repr(e)
        ))
    
    # if flights is None:
    #     flight_info = airportinfo.flight_info( icao24 )
    #     print( flight_info )
    #     return format_airportinfo_flight( flight_info )


# print( get_flight_info( callsign="XOJ747") )
bbox = tuple( opensky.config["bbox"] )

print( "hello")

last_seen_icao24 = None
while True:

    # 51.448834, -0.140049
    # 51.400140, 0.015570
    # https://opensky-network.org/api/states/all?lamin=51.400140&lomin=-0.140049&lamax=51.448834&lomax=0.015570
    # r = opensky.get_states(bbox=(51.400140, 51.448834, -0.140049, 0.015570))
    # r = opensky.get_states()

    try:

        r = opensky.get_states( bbox=bbox )
        # print( r )
        #r = opensky.get_states()
    
        if (r is not None) and r.states:
            
            for state in r.states: 

                # print( state )

                timestamp = state.time_position
                if timestamp is None:
                    timestamp = time.time()
                callsign = state.callsign.strip()
                icao24 = state.icao24.strip()

                print( "***\n{}: Found a flight ({}) with callsign {}".format(
                    datetime.datetime.fromtimestamp( timestamp ),
                    icao24,
                    callsign
                ))
                
                if icao24 and (icao24 != last_seen_icao24):
                    flight_info = get_flight_info( icao24=icao24, callsign=callsign, timestamp=timestamp )
                    if flight_info is not None:
                        print( flight_info )
                        last_seen_icao24 = icao24

                break
                        
    
    except Exception as e:
        print( repr(e) )
        pass

    time.sleep( 30.0 )  

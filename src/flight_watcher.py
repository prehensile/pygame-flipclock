import requests
import time
import json
import datetime

import random

import airports
import flightaware
import opensky


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


def format_opensky_flight( j ):
    return format_flight(
        dep_icao = j["estDepartureAirport"],
        arr_icao = j["estArrivalAirport"],
        callsign = j["callsign"]
    )


def format_flightaware_flight( f ):
    return format_flight(
        dep_icao = f['origin'],
        arr_icao = f['destination'],
        callsign = f['ident']
    )

bbox = tuple( opensky.config["bbox"] )


def get_flight_info( icao24=None, callsign=None, timestamp=None ):
    
    flights = None
    if timestamp is None:
        timestamp = int( time.time() )
                    
    # first, attempt to get flight info from opensky
    try:
        print( "-> attempt to get flight info from opensky")
        flights = opensky.get_flights(
            icao24 = icao24,
            begin = timestamp - flight_window,
            end = timestamp + flight_window
        )
        print( "--> flights: {}".format( repr(flights)) )
        if flights is not None:
            #for flight in flights:
                # print_opensky_flight( flight )?
            return format_opensky_flight( flights[-1] )
    except Exception as e:
        return( "opensky.get_flights failed: {}".format(
            repr(e)
        ))

    # if that fails, try flightaware
    if (flights is None) or len(flights) < 1:
        print( "-> attempt to get flight info from flightaware")
        try:
            flights = flightaware.flight_info( callsign )
            #print( flights )
        # for flight in flights:
        #     print_flightaware_flight( flight )
            return format_flightaware_flight( flights[-1] )
        except Exception as e:
            return( "flightaware.flight_info failed: {}".format(
            repr(e)
        ))
        

print( "DEBUG: {}".format( get_flight_info( icao24="3c71a4", callsign="BCS395", timestamp=int(time.time()) ) ) )

last_seen_icao24 = None
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

                # print( state )

                timestamp = state.time_position
                if timestamp is None:
                    timestamp = time.time()
                callsign = state.callsign
                icao24 = state.icao24

                print( "{}: Found a flight ({}) with callsign {}".format(
                    datetime.datetime.fromtimestamp( timestamp ),
                    icao24,
                    callsign
                ))
                
                if icao24 and (icao24 != last_seen_icao24):
                    print( get_flight_info( icao24=icao24, callsign=callsign, timestamp=timestamp ) )
                    last_seen_icao24 = icao24
                        
    
    except Exception as e:
        # print( repr(e) )
        pass

    time.sleep( 30.0 )  

import requests
import time
import json
import datetime
import logging
import sys

import random

import airports
import flightaware
import opensky
import airportinfo
import aviationstack


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
    print( f )
    return format_flight(
        dep_icao = f['origin'],
        arr_icao = f['destination'],
        callsign = f['ident']
    )


def format_airportinfo_flight( f ):
    return format_flight(
        dep_icao = f['departure_icao_code'],
        arr_icao = f['arrival_icao_code'],
        callsign = f['flight_icao_number']
    )



def whittle_flightaware_flights( flights ):
    candidate_flight = flights[-1]
    ptr = len( flights ) -1
    while ptr > -1:
        c = flights[ ptr ]
        o = c['origin']
        d = c['destination']
        if (d is not None) and (o is not None) and (len(o) > 0) and (len(d)>0):
            break
        ptr -= 1
    return candidate_flight




def flight_info_opensky( icao24, timestamp ):
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


def formatted_flight_info_flightaware( callsign ):
    logging.debug( "-> attempt to get flight info from flightaware")
    flights = flightaware.flight_info( callsign, how_many=3 )
    logging.debug( flights )
# for flight in flights:
#     print_flightaware_flight( flight )
    return format_flightaware_flight( whittle_flightaware_flights( flights ) )


def flight_info_aviationstack( icao24 ):
    flights = aviationstack.get_flights( icao24 )
    f = flights[0]
    return format_flight(
        dep_icao = f['departure']['icao'],
        arr_icao = f['arrival']['icao'],
        callsign = f['flight']['icao']
    )



def get_flight_info( icao24=None, callsign=None, timestamp=None ):
    
    flights = None
    if timestamp is None:
        timestamp = int( time.time() )
                    
    # first, attempt to get flight info from opensky
    # try:
    #     return flight_info_opensky()
    # except Exception as e:
    #     return( "opensky.get_flights failed: {}".format(
    #         repr(e)
    #     ))


    # if that fails, try flightaware
    if (flights is None) or len(flights) < 1:
        try:
            flights = flightaware.combined_flight_info( callsign )
            if (flights is not None) and len( flights ) > 0:
                return format_flightaware_flight(
                    whittle_flightaware_flights( flights )
                )
        except Exception as e:
            raise
            return( "flightaware.flight_info failed: {}".format(
                repr(e)
            ))
    
    if (flights is None) or len(flights) < 1:
        try:
            print( "fallback to aviationstack")
            return flight_info_aviationstack( callsign )
        except Exception as e:
            return( "flight_info_aviationstack failed: {}".format(
                repr(e)
            ))
    
    # if flights is None:
    #     flight_info = airportinfo.flight_info( icao24 )
    #     print( flight_info )
    #     return format_airportinfo_flight( flight_info )


# print( get_flight_info( callsign="XOJ747") )
bbox = tuple( opensky.config["bbox"] )

print( "hello")
if len(sys.argv) > 0:
    ident = sys.argv[1]
    print( get_flight_info( callsign=ident) )


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

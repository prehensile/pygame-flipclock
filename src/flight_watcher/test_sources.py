import sys
import logging

from sources import flightradar24, opensky, airportinfo, aviationstack, flightaware

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_source( test_func, callsign ):
    try:
        print( list(test_func( callsign )) )
    except Exception as e:
        print( repr(e) )


def test_callsign( callsign ):

    test_source( flightradar24.flight_info, callsign )
    test_source( airportinfo.flight_info, callsign )
    test_source( aviationstack.get_flights, callsign )
    test_source( flightaware.flight_info, callsign )

    try:
        print( list(flightradar24.flight_info( callsign )) )
    except Exception as e:
        print( repr(e) )

    try:
        print( opensky.get_route(callsign)['route'] )
    except Exception as e:
        print( repr(e) )


callsigns = [ "BAW56", "QY977" ]
if len(sys.argv) > 1 :
    callsigns = [sys.argv[1]]

for callsign in callsigns:
    print( "***" )
    test_callsign( callsign )



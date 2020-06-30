import sys
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

callsign = sys.argv[1]

from sources import flightradar24, opensky

try:
    print( list(flightradar24.flight_info( callsign )) )
except Exception as e:
    print( repr(e) )

try:
    print( opensky.get_route(callsign)['route'] )
except Exception as e:
    print( repr(e) )


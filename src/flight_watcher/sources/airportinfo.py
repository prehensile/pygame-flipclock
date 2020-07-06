import re
import json
import sys
import logging

import cloudscraper
import requests

from ..model import Flight, Airport
from ..sources import utils


def parse_flight( o ):
    # return(
    #     Flight(
    #         Airport( o['departure_icao_code'] ),
    #         Airport( o['arrival_icao_code'] )
    #     )
    # )
    return utils.parse_flight(
        o, "departure_icao_code", "arrival_icao_code"
    )



def flight_info( callsign ):
    url = "https://airportinfo.live/flight/%s" % callsign
    print( url )
    scraper = cloudscraper.create_scraper()
    r = scraper.get( url )
    m = re.search( "var flightdata = (.*);", r.text )
    o = json.loads( m.group(1) )
    return(
        [parse_flight(o)]
    )

if __name__ == "__main__":
    callsign = sys.argv[1]
    print( flight_info(callsign) )

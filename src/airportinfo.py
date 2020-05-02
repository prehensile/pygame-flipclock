import requests
import re
import cloudscraper
import json
import sys

def flight_info( callsign ):
    # s = requests.Session()
    # r = s.get(
    #     "https://airportinfo.live/flight/%s" % callsign
    # )
    # print( r )
    # print( r.text )
    # m = re.search( "var flightdata = (.*);", r.text )
    # print( m )
    url = "https://airportinfo.live/flight/%s" % callsign
    print( url )
    scraper = cloudscraper.create_scraper()
    r = scraper.get( url )
    m = re.search( "var flightdata = (.*);", r.text )
    o = json.loads( m.group(1) )
    # print( o )
    return( o )

if __name__ == "__main__":
    callsign = sys.argv[1]
    print( flight_info(callsign) )

import requests

from model import Flight, Airport


def flight_info( callsign ):
    r = requests.get(
        "https://api.flightradar24.com/common/v1/flight/list.json",
        params = {
            "fetchBy" : "flight",
            "page" : 1,
            "limit" : 25,
            "query" : callsign
        },
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
        }
    )
    
    j = r.json()

    flights = map(
        lambda f: Flight(
            Airport( f["airport"]["origin"]["code"]["icao"] ),
            Airport( f["airport"]["destination"]["code"]["icao"] )
        ),
        j["result"]["response"]["data"]
    )

    return flights


if __name__ == "__main__":
    import sys
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    callsign = sys.argv[1]
    print( flight_info( callsign ) )
import requests

from ..model import Airport, Flight
from ..sources import utils


def parse_flights( j ):

    # return map(
    #     lambda f: Flight(
    #         Airport( f["airport"]["origin"]["code"]["icao"] ),
    #         Airport( f["airport"]["destination"]["code"]["icao"] )
    #     ),
    #     j["result"]["response"]["data"]
    # )

    return utils.parse_flights(
        j["result"]["response"]["data"],
        "airport.origin.code.icao",
        "airport.destination.code.icao"
    )


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
    return parse_flights( j )


if __name__ == "__main__":
    import sys
    callsign = sys.argv[1]
    print( flight_info( callsign ) )
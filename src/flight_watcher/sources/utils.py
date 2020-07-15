import logging

from ..model import Airport, Flight
from flight_watcher import airports


def init_logging( log_level=logging.DEBUG, log_level_requests=logging.INFO ):
    logging.basicConfig()
    logging.getLogger().setLevel( log_level )
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel( log_level_requests )
    requests_log.propagate = True


def retrieve_value( source_object, key ):
    path = key.split( "." )
    val = source_object
    for k in path:
        val = val[k]
    return val


def flight_for_icaos( origin_icao, destination_icao ):
    origin = None
    destination = None
    if len(origin_icao) > 1:
        origin = airports.airport_for_icao( origin_icao )
    if len(destination_icao) > 1:
        destination = airports.airport_for_icao( destination_icao )

    return Flight( origin, destination )


def parse_flight( source_object, origin_key, destination_key ):

    logging.debug(  "parse_flight: %s", source_object )

    origin_icao = None
    destination_icao = None

    try:
        origin_icao = retrieve_value( source_object, origin_key )
    except Exception as e:
        logging.exception( e )
    
    try:
        destination_icao = retrieve_value( source_object, destination_key )
    except Exception as e:
        logging.exception( e )
    
    return flight_for_icaos( origin_icao, destination_icao )


def parse_flights( flights, origin_key, destination_key ):
    out = []
    for f in flights:
        out.append(
           parse_flight( f, origin_key, destination_key )
        )
    return out


if __name__ == "__main__":
    j = """
    {
        "test" : {
            "one" : {
                "two" : {
                    "three" : "hi there!"
                }
            }
        }
    }
    """
    import json
    o = json.loads( j )
    v = retrieve_value( o, "test.one.two.three" )
    print( v )
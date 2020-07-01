import logging

from model import Airport, Flight


def init_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def retrieve_value( source_object, key ):
    path = key.split( "." )
    val = source_object
    for k in path:
        val = val[k]
    return val


def parse_flight( source_object, origin_key, destination_key ):
    origin = None
    destination = None

    try:
        origin = retrieve_value( source_object, origin_key )
    except Exception as e:
        logging.exception( e )
    
    try:
        destination = retrieve_value( source_object, destination_key )
    except Exception as e:
        logging.exception( e )

    return Flight( Airport(origin), Airport(destination) )


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
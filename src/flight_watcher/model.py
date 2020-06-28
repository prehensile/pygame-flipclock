from collections import namedtuple

Airport = namedtuple( "Airport", ("icao") )
Flight = namedtuple( "Flight", ("origin","destination") )
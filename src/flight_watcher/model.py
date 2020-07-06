import logging
from collections import namedtuple


class Airport( object ):
    def __init__( self, icao=None, iata=None, name=None, country=None ):
        logging.debug( "Airport: %s %s %s %s", icao, iata, name, country )
        self.icao = icao
        self.iata = iata
        self.name = name
        self.country = country 
    
    def format( self ):
        return "{} ({}, {})".format(
            self.iata,
            self.name,
            self.country
    )


Flight = namedtuple( "Flight", ("origin","destination") )
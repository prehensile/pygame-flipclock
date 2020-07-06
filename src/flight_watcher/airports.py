import logging
import os
import sqlite3

from .model import Airport


def connect_db():
    pth = os.path.dirname( __file__ )
    pth = os.path.join( pth, "data/airports.sqlite" )
    conn = sqlite3.connect( pth, check_same_thread=False )
    return conn.cursor()

cur = None

def airport_for_icao( icao ):
    logging.debug( "airport_for_icao: %s" % icao )
    global cur
    if cur is None:
        cur = connect_db()
    cur.execute( 'SELECT * FROM airports WHERE icao=?', (icao,) )
    record = cur.fetchone()
    print( record )
    a = Airport(
        icao = icao,
        iata = record[1],
        name = record[2],
        country = record[3]
    )
    print( a )
    print( a.format() )
    return a

import sqlite3

conn = sqlite3.connect( "data/airports.sqlite")
cur = conn.cursor()

def airport_for_icao( icao ):
    cur.execute( 'SELECT * FROM airports WHERE icao=?', (icao,) )
    return cur.fetchone()


def format_airport( airport ):
    return "{} ({}, {})".format(
        airport[1],
        airport[2],
        airport[3]
    )


def formatted_airport_for_icao( icao ): 
    return format_airport( airport_for_icao(icao) )

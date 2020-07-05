import sqlite3

from model import Airport


conn = sqlite3.connect( "data/airports.sqlite", check_same_thread=False )
cur = conn.cursor()

def airport_for_icao( icao ):
    cur.execute( 'SELECT * FROM airports WHERE icao=?', (icao,) )
    record = cur.fetchone()
    return Airport(
        icao = icao,
        iata = record[1],
        name = record[2],
        country = record[3]
    )

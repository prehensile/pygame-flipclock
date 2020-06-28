import sqlite3

conn = sqlite3.connect('airports.sqlite')

c = conn.cursor()

c.execute('''CREATE TABLE airports
             (icao text, iata text, name text, country text)''')


with open( 'airports.dat' ) as fp:
    for line in fp.readlines():
        fields = line.split(",")
        icao = fields[5].strip('"')
        iata = fields[4].strip('"')

        if iata == "\\N":
            continue

        name = fields[2].strip('"')
        country = fields[3].strip('"')
        c.execute(
            'INSERT INTO airports VALUES (?,?,?,?)',
            (
                icao,
                iata,
                name,
                country
            )
        )

conn.commit()
conn.close()
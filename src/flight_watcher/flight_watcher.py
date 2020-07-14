import datetime
import json
import logging
import random
import sys
import threading
import time
from collections import defaultdict

import requests

import airports
from model import Airport, Flight
from sources import (airportinfo, aviationstack, flightaware, flightradar24,
                     opensky, utils)


def format_flight( flight, callsign=None  ):

    if flight is None:
        return

    dep_airport = None
    arr_airport = None

    if( flight.origin ):
        dep_airport = flight.origin.format()
    
    if( flight.destination ):
        arr_airport = flight.destination.format()
   
    return "{}: {} from {} to {}".format(
        datetime.datetime.now(),
        callsign.strip(),
        dep_airport,
        arr_airport   
    )


flight_window = 60 * 60 * 24
poll_interval = 30.0


class FlightWatcher( object ):


    def __init__( self ):
        self.success_counts = defaultdict( int )
        self.latest_flights = None


    def whittle_flights( self, flights ):
        if flights is None:
            return
        for flight in flights:
            o = flight.origin
            d = flight.destination
            if (d is not None) or (o is not None):
                return flight


    def get_flight_info( self, icao24=None, callsign=None, timestamp=None ):
        
        if timestamp is None:
            timestamp = int( time.time() )
                        
        # first, attempt to get route info from opensky
        try:
            print( "Attempt to get route info from opensky")
            r = opensky.get_route( callsign )
            route = r["route"]
            self.success_counts[ "opensky-routes" ] += 1
            return [
                utils.flight_for_icaos( route[0], route[-1] )
            ]
        except Exception as e:
            print( "opensky.get_route failed: {}".format(
                repr(e)
            ))
        

        # if that fails, attempt to get flight info from opensky
        try:
            print( "Attempt to get flight info from opensky")
            flights = opensky.get_flights(
                icao24 = icao24,
                begin = timestamp - flight_window,
                end = timestamp + flight_window
            )
            if len( flights ) > 0: 
                self.success_counts[ "opensky-flights" ] += 1
                # opensky flights have the newest at the end of the list
                return reversed( flights )
        except Exception as e:
            print( "opensky.get_flights failed: {}".format(
                repr(e)
            ))


        try:
            print( "fallback to flightradar24")
            flights = flightradar24.flight_info( callsign )
            if len( flights ) > 1:
                return flights
        except Exception as e:
            print( "flight_info_flightradar24 failed: {}".format(
                repr(e)
            ))


        # if that fails, try flightaware
        try:
            print( "fallback to flightaware")
            flights = flightaware.flight_info( callsign, how_many=3 )
            if len( flights ) > 0:
                self.success_counts[ "flightaware" ] += 1
                return flights
        except Exception as e:
            print( "flightaware.flight_info failed: {}".format(
                repr(e)
            ))
        
        try:
            print( "fallback to aviationstack")
            flights = aviationstack.get_flights( icao24 )
            if len( flights ) > 1:
                self.success_counts[ "aviationstack" ] += 1
                return flights
        except Exception as e:
            print( "flight_info_aviationstack failed: {}".format(
                repr(e)
            ))
        
        # if flights is None:
        #     flight_info = airportinfo.flight_info( icao24 )
        #     print( flight_info )
        #     return format_airportinfo_flight( flight_info )

        self.success_counts[ "failure" ] += 1
    

    def on_callsign_received( self, icao24=None, callsign=None, timestamp=None ):
        flights = self.get_flight_info( icao24=icao24, callsign=callsign, timestamp=timestamp )
        if flights is not None:
            flight = self.whittle_flights( flights )
            print( flight )
            if flight is not None:
                print( format_flight( flight, callsign ) )
                self.push_flight( flight )


    def pop_flights( self ):
        f = self.latest_flights
        self.latest_flights = []
        return f
    

    def push_flight( self, flight ):
        if self.latest_flights is None:
            self.latest_flights = []
        self.latest_flights.append( flight )


    def is_running( self ):
        return self.running
    

    def set_running( self, r ):
        self.running = r


    def run( self, bbox=None ):
        
        last_seen_icao24 = None
        self.set_running( True )
        last_poll_time = 0.0

        while self.is_running():

            # 51.448834, -0.140049
            # 51.400140, 0.015570
            # https://opensky-network.org/api/states/all?lsamin=51.400140&lomin=-0.140049&lamax=51.448834&lomax=0.015570
            # r = opensky.get_states(bbox=(51.400140, 51.448834, -0.140049, 0.015570))
            # r = opensky.get_states()

            t = time.time()
            if (t - last_poll_time) < poll_interval:
                continue

            try:

                r = opensky.get_states( bbox=bbox )
                #r = opensky.get_states()
            
                if (r is not None) and r.states:
                    
                    for state in r.states: 

                        timestamp = state.time_position
                        if timestamp is None:
                            timestamp = time.time()
                        callsign = state.callsign.strip()
                        icao24 = state.icao24.strip()

                        print( "***\n{}: Found a flight ({}) with callsign {}".format(
                            datetime.datetime.fromtimestamp( timestamp ),
                            icao24,
                            callsign
                        ))
                        
                        if icao24 and (icao24 != last_seen_icao24):
                            self.on_callsign_received( icao24=icao24, callsign=callsign, timestamp=timestamp )
                            last_seen_icao24 = icao24
                            print( "successes: " + repr(self.success_counts) )

            
            except Exception as e:
                logging.exception(e)

            last_poll_time = time.time()  


class FlightWatcherThreadedRunner( FlightWatcher ):

    def push_flight( self, flight ):
        # print( "FlightWatcherThreadedRunner.push_flight")
        if self.latest_flights is None:
            q = None
            try:
                from queue import Queue
                q = Queue()
            except ImportError as e:
                import Queue
                q = Queue.Queue()
            self.latest_flights = q
        self.latest_flights.put( flight )
    

    def pop_flights( self ):
        # logging.debug( "FlightWatcherThreadedRunner.pop_flights")
        out = []
        if self.latest_flights is not None:
            while not self.latest_flights.empty():
                out.append( self.latest_flights.get() )
        return out


    def stop( self ):
        self.set_running( False )
    

    def set_running( self, r ):
        if not hasattr( self, "running" ):
            self.running = threading.Event()
        if r:
            self.running.set()
        else:
            self.running.clear()
    

    def is_running( self ):
        return self.running.isSet()


class FlightWatcherThreaded( threading.Thread ):
    
    @property
    def runner( self ):
        if not hasattr( self, "_runner" ):
            self._runner = FlightWatcherThreadedRunner()
        return self._runner


    def run( self ):

        utils.init_logging()
        logging.debug( "FlightWatcherThreaded.run" )
        
        bbox = None
        if hasattr( self, "bbox" ):
            bbox = self.bbox

        self.runner.run( bbox )
    

    def set_bbox( self, bbox ):
        self.bbox = bbox


    def pop_flights( self ):
        return self.runner.pop_flights()
    

    def stop( self ):
        self.runner.stop()
    

    # used for simulating an incoming callsign during testing
    def on_callsign_received( self, icao24=None, callsign=None, timestamp=None ):
        self.runner.on_callsign_received( icao24=icao24, callsign=callsign, timestamp=timestamp )


    def init_logging( self ):
        utils.init_logging()


bbox = tuple( opensky.config["bbox"] )

def run_blocking():
    watcher = FlightWatcher()

    # utils.init_logging()

    print( "hello")
    if len(sys.argv) > 1:
        callsign = sys.argv[1]    
        flights = watcher.get_flight_info( callsign=callsign, icao24="4ca6c4" )
        flight = watcher.whittle_flights( flights )
        print( flight )
        print( format_flight( flight, callsign ) )
    
    watcher.run( bbox=bbox )


def run_threaded():
   
    #utils.init_logging()

    watcher = FlightWatcherThreaded()
    watcher.set_bbox( bbox )
    watcher.start()
   
    try:
        while True:
            flights = watcher.pop_flights()
            if (flights is not None) and (len(flights) > 0):
                print( flights )
    except KeyboardInterrupt:
        print( "KeyboardInterrupt" )
        pass

    watcher.stop()
    watcher.join()




if __name__ == "__main__":
    run_blocking()
   #run_threaded()

#!/usr/bin/env python

import pygame
import sys
import os
import random
import re
import time
import datetime


class ClockDisplay():


    def __init__( self, image_path ):
        
        self.ts_age = 0
        self.last_hour = 0
        self.last_minute = 0

        self.load_images( image_path )
        self.init_pygame()
        self.display_time( 0, 0 )
        


    def init_pygame( self, native_width=480, native_height=272 ):

        self.background_colour = ( 255,255,255 )
        self.fps = 8

        pygame.init()
        
        display_info = pygame.display.Info()
        w = display_info.current_w
        h = display_info.current_h
        self.window_size=(w,h)

        if (w <= native_width) or (h <= native_height):
            self.window = pygame.display.set_mode( self.window_size, pygame.FULLSCREEN )  
        else:
            self.window = pygame.display.set_mode( (native_width, native_height) )
        
        self.surface = pygame.display.get_surface()
        
        pygame.mouse.set_visible( False )

        self.clock = pygame.time.Clock()


    def load_images( self, image_path ):
        images = []
        for i in range(10):
            fn_image = "%d.png" % i
            images.append(
                pygame.image.load(
                    os.path.join( image_path, fn_image )
                )
            )
        self.number_surfaces = images

    
    SEGMENT_BOTH = 0
    SEGMENT_UPPER = 1
    SEGMENT_LOWER = 2
    def display_number( self, number, pos, segment=SEGMENT_BOTH ):
        img = self.number_surfaces[ number ]
        area = img.get_clip()
        offs = [0,0]
        if segment == self.SEGMENT_UPPER:
            area.height /=2
        elif segment == self.SEGMENT_LOWER:
            hh = area.height /2
            area.top = hh
            area.height = hh
            offs[1] = hh
        self.window.blit( img, (pos[0]+offs[0],pos[1]+offs[1]), area=area )


    PADDING = 8
    SPACING = 116
    def display_numbers( self, numbers, segment=SEGMENT_BOTH ):
        pos = [self.PADDING,self.PADDING]
        for n in numbers:
            self.display_number( n, pos, segment=segment )
            pos[0] += self.SPACING


    def numbers_for_time( self , hour, minute ):
        h = "%02d" % hour
        m = "%02d" % minute
        return [ int(h[0]), int(h[1]), int(m[0]), int(m[1]) ]


    def display_time( self, hour, minute ):

        # draw_half will be set if the time changes. used for cheap animation on change.
        draw_half = False
        # keep track of how long we've been displaying a given timestamp
        self.ts_age += 1
        if (minute != self.last_minute) or (hour != self.last_hour):
            self.ts_age = 0
            draw_half = True

        self.window.fill( self.background_colour )
        
        numbers = self.numbers_for_time( hour, minute )
        if draw_half:
            # if time has changed, for this frame draw new time in the top half...
            self.display_numbers( numbers, segment=self.SEGMENT_UPPER )
            # ... and old time in the bottom half for cheap flip effect
            numbers_last = self.numbers_for_time( self.last_hour, self.last_minute )
            self.display_numbers( numbers_last, segment=self.SEGMENT_LOWER )
        else:
            # otherwise, just draw the time
            self.display_numbers( numbers, segment=self.SEGMENT_BOTH )
        
        # draw split line down the horizontal middle
        pygame.draw.line( self.window, self.background_colour, (0,136-1), (480,136-1), 2 )

        self.last_minute = minute
        self.last_hour = hour


    def update( self, dt ):

        self.display_time( dt.hour, dt.minute )    
        pygame.display.flip()

        # handle exits
        was_quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                was_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    was_quit = True
        
        if not was_quit:
            self.clock.tick( self.fps )
        
        return was_quit



if __name__ == '__main__':
    cd = ClockDisplay( os.path.realpath( "./images" ) )
    
    was_quit = False
    fps = 50
    while not was_quit:
        dt = datetime.datetime.now()
        was_quit = cd.update( dt )
        
        

        

    





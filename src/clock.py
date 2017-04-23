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
        
        p = (pos[0]+offs[0],pos[1]+offs[1])
        self.window.blit( img, p, area=area )

        # draw a translucent black rect over *most* of a changing segement
        # cheap, hacky transition effect!
        if segment == self.SEGMENT_UPPER:
            yo = 10
            r = pygame.Rect( (p[0],p[1]+yo), (area.width,area.height-yo) )
            brightness = 128 + 64
            self.window.fill( (brightness,brightness,brightness), rect=r, special_flags=pygame.BLEND_MULT )


    PADDING = 8
    SPACING = 116
    def display_numbers( self, numbers, segment=SEGMENT_BOTH, mask=None ):
        pos = [self.PADDING,self.PADDING]
        i = 0
        for n in numbers:
            if n is not None:
                if (mask is None) or (mask and mask[i]):
                    self.display_number( n, pos, segment=segment )    
            pos[0] += self.SPACING
            i += 1


    def numbers_for_time( self , hour, minute ):
        h = "%02d" % hour
        m = "%02d" % minute
        return [ int(h[0]), int(h[1]), int(m[0]), int(m[1]) ]


    def mask_for_numbersets( self, numbers, numbers_last ):
        mask = [ False for n in numbers ]
        for i in range( len(numbers_last) ):
            if numbers_last[i] != numbers[i]:
                mask[i] = True
        return mask


    def display_time( self, hour, minute ):

        # has_changed will be set if the time changes. used for cheap animation on change.
        has_changed = False
        # keep track of how long we've been displaying a given timestamp
        self.ts_age += 1
        if (minute != self.last_minute) or (hour != self.last_hour):
            self.ts_age = 0
            has_changed = True

        self.window.fill( self.background_colour )
        
        numbers = self.numbers_for_time( hour, minute )
        # default mask - draw everything
        mask = [ True for i in range(len(numbers)) ]

        if has_changed:

            # draw changed numbers

            numbers_last = self.numbers_for_time( self.last_hour, self.last_minute )
            
            # calculate mask for changed numbers
            mask = self.mask_for_numbersets( numbers, numbers_last )

            # if time has changed, for this frame draw new time in the top half...
            self.display_numbers( numbers, segment=self.SEGMENT_UPPER, mask=mask )
            # ... and old time in the bottom half for cheap flip effect
            self.display_numbers( numbers_last, segment=self.SEGMENT_LOWER, mask=mask )
            
            # invert mask so that main draw will pick up everything that's not changed  
            mask = [ not m for m in mask ]
        
        # draw unchanged numbers
        self.display_numbers( numbers, segment=self.SEGMENT_BOTH, mask=mask )
        
        # draw split line down the horizontal middle
        pygame.draw.line( self.window, self.background_colour, (0,136-1), (480,136-1), 2 )

        self.last_minute = minute
        self.last_hour = hour


    def update( self, dt, fps=8 ):

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
            self.clock.tick( fps )
        
        return was_quit



if __name__ == '__main__':

    # get containing path of this script
    pth_self = os.path.realpath(
        os.path.dirname( __file__ ) 
    )

    # start new clock display, using this path
    cd = ClockDisplay(
        os.path.join( pth_self, "./images" )
    )
    
    # main runloop
    was_quit = False
    fps = 8
    while not was_quit:
        dt = datetime.datetime.now()
        was_quit = cd.update( dt, fps=fps )
        
        

        

    





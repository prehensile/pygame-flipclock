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
        self.load_images( image_path )
        self.init_pygame()
        self.display_time( 0, 0 )


    def init_pygame( self, native_width=480, native_height=272 ):

        self.background_colour = ( 255,255,255 )
        self.fps = 50

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
        for i in range(9):
            fn_image = "%d.png" % i
            print fn_image
            images.append(
                pygame.image.load(
                    os.path.join( image_path, fn_image )
                )
            )
        self.number_surfaces = images


    def display_time( self, hours, minutes ):
        self.window.fill( self.background_colour )
        h = "%02d" % hours
        
        img = self.number_surfaces[ int(h[0]) ]
        self.window.blit( img, (8,8) )

        img = self.number_surfaces[ int(h[1]) ]
        self.window.blit( img, (124,8) )

        m = "%02d" % minutes

        img = self.number_surfaces[ int(m[0]) ]
        self.window.blit( img, (240,8) )

        img = self.number_surfaces[ int(m[1]) ]
        self.window.blit( img, (356,8) )

        pygame.draw.line( self.window, self.background_colour, (0,136-1), (480,136-1), 2 )


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
        
        

        

    





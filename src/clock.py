#!/usr/bin/env python

import datetime
import os
import random
import re
import sys
import time

import pygame
from pygame import display, draw


class DigitCache( object ):
    
    images = {}
    image_path = "images"

    @classmethod
    def image_for_character( cls, c ):
        if c not in cls.images:
            
            pth_image = os.path.join(
                cls.image_path,
                "{}.png".format( c )
            )
            
            if not os.path.exists(pth_image):
                # fallback to hex representation of unicode point
                pth_image = os.path.join(
                cls.image_path,
                "{}.png".format( hex(ord(c)) )
            )
            
            cls.images[c] = pygame.image.load(
                pth_image
            )
        return cls.images[c]


class ClockDigit( object ):

    def __init__( self ):
        self.image = None
        self.next_image = None
        self.transition_frame = 0
        self.current_character = None
        self.transition_delay = 0
        self.is_dirty = False


    def set_image( self, img ):
        if img != self.image:
            self.area = img.get_clip()
            if self.image is None:
                self.image = img
            else:
                self.next_image = img
                self.transition_frame = 1
            self.is_dirty = True
        


    def set_character( self, c, delay=0 ):
        if c != self.current_character:
            self.set_image( DigitCache.image_for_character(c) )
            self.current_character = c
            self.transition_delay = delay
            return True
        return False


    def draw( self, window, x, y ):
       
        window.blit( self.image, (x,y), area=self.area )

        if self.transition_delay > 0:
            self.transition_delay -= 1
        
        elif (self.transition_frame > 0) and (self.next_image is not None):
           
            if self.transition_frame == 1:

                brightness = 128 + 64
               
                # first frame of transition: top half of digit is new image, bottom half is old
                r = self.next_image.get_clip()
                r.height /=2
                #r.top = r.height/2
                window.blit( self.next_image, (x,y), r )
                r.x = x
                r.y = y
                window.fill( (brightness,brightness,brightness), rect=r, special_flags=pygame.BLEND_MULT )
            
            self.transition_frame +=1

            if self.transition_frame == 2:
                self.image = self.next_image
            
            elif self.transition_frame == 3:
                self.is_dirty = False
                self.transition_frame = 0
                self.next_image = None


    def width( self ):
        if self.image:
            if self.area:
                return self.area.width
            return self.image.get_width()
        return 0



class NuDisplay( object ):

    def __init__( self, num_digits=4 ):
        self.digits = []
        self.padding_x = 8
        for i in range( num_digits ):
            self.digits.append( ClockDigit() )


    def draw( self, window, x=0, y=0 ):
        for d in self.digits:
            d.draw( window, x, y )
            x += d.width() + self.padding_x

    
    def display_string( self, str ):
        delay = 0
        for i, d in enumerate(self.digits):
            will_change = d.set_character( str[i], delay=delay )
            if will_change:
                delay += 1


    def is_dirty( self ):
        dirty = False
        for d in self.digits:
            dirty = dirty or d.is_dirty
        return dirty



class PygameHandler( object ):

    def initialize( self, native_width=480, native_height=272 ):

        pygame.init()
        
        display_info = pygame.display.Info()
        w = display_info.current_w
        h = display_info.current_h
        window_size=(w,h)
        window = None

        if (w <= native_width) or (h <= native_height):
            window = pygame.display.set_mode( window_size, pygame.FULLSCREEN )  
        else:
            window = pygame.display.set_mode( (native_width, native_height) )
        
        self.window = window
        self.surface = pygame.display.get_surface()
        
        pygame.mouse.set_visible( False )

        return self.window, self.surface


    def was_quit( self ):
        was_quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                was_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    was_quit = True
        return was_quit


bg_color = (255,255,255) 

def update_display( window, surface, sr, d ):
    if d.is_dirty():
        window.fill( bg_color )
        d.draw( window, 4, 8 )
        # draw split line down the horizontal middle
        pygame.draw.line( window, bg_color, (0,(sr.height/2)-1), (sr.width,(sr.height/2)-1), 2 )
        pygame.display.flip()


def main():

    ph = PygameHandler()
    window, surface = ph.initialize()
    sr = surface.get_rect()
    d = NuDisplay()
    
    d.display_string("HLLO")

    update_display( window, surface, sr, d )
    time.sleep( 3.0 )

    q = False
    last_string = None
    fps = 12.0  
    while not q:
        dt = datetime.datetime.now()
        ds = "{:02d}{:02d}".format( dt.second, dt.second )
        if ds != last_string:
            d.display_string( ds )
            last_string = ds
        
        update_display( window, surface, sr, d )
        
        q = ph.was_quit()
        if not q:
            time.sleep( 1.0 / fps )


if __name__ == '__main__':
    main()
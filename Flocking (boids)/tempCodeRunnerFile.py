import pygame as pg
import sys
from random import uniform
from Boids import Boids, Boid  # assuming your classes are in Boid.py
from Settings import *

def main():
    pg.init()
    screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()
    
    flock = Boids()
    
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        
        screen.fill(SCREENCOLOR)
        flock.update(screen)
        pg.display.flip()
        clock.tick(FPS)
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
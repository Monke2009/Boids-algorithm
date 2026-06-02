import pygame as pg
import sys
from random import uniform
from Boids import Boids, Boid
from Settings import *

def main():
    pg.init()
    screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()
    
    flock = Boids()
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEWHEEL:
                # event.y: 1 = up, -1 = down
                flock.scale_radius += event.y
                flock.scale_radius = max(0, min(flock.scale_radius, SELECT_RADIUS_CAP))

        screen.fill(SCREENCOLOR)
        flock.handle_chunk_edit()
        flock.draw_chunks(screen)
        flock.update(screen)
        flock.draw_hud(screen)
        if flock.controls: flock.draw_instructions(screen)
        pg.display.flip()
        clock.tick(FPS)
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()

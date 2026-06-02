from Settings import *
from random import uniform
import pygame as pg
import math

class Boid:
    def __init__(self):
        # Give initial random velocity so they move from the start
        self.velocity = Vector2(uniform(-MAXSPEED, MAXSPEED), uniform(-MAXSPEED, MAXSPEED))
        self.position = Vector2(uniform(0, SCREENWIDTH), uniform(0, SCREENHEIGHT))
        self.chunk_coords = None
        
    def update_chunk(self):
        return (int(self.position.x // CHUNK_SIZE), 
                int(self.position.y // CHUNK_SIZE))

    def limit_velocity(self):
        speed = math.hypot(self.velocity.x, self.velocity.y)
        if speed > MAXSPEED:
            self.velocity = self.velocity.multiply(MAXSPEED / speed)
        if speed < MINSPEED:
            self.velocity = self.velocity.multiply(MINSPEED / speed)

    def draw(self, screen):
        if self.velocity.length() < 0.01:
            angle = 0
        else:
            angle = math.atan2(self.velocity.y, self.velocity.x)
        
        # Triangle relative to center (tip points right = 0 radians)
        tip = Vector2(BOID_SIZE * 2, 0)
        left_corner = Vector2(-BOID_SIZE * 1.5, -BOID_SIZE)
        right_corner = Vector2(-BOID_SIZE * 1.5, BOID_SIZE)
        
        # Rotate and translate
        tip = self.position.add(tip.rotate(angle))
        left = self.position.add(left_corner.rotate(angle))
        right = self.position.add(right_corner.rotate(angle))
        
        points = [(tip.x, tip.y), 
                (left.x, left.y), 
                (right.x, right.y)]
        pg.draw.polygon(screen, WHITE, points)

class Boids:
    def __init__(self):
        self.boidlist = []


        self.chunk_cols = SCREENWIDTH//CHUNK_SIZE
        self.chunk_rows = SCREENHEIGHT//CHUNK_SIZE
        self.chunks = [[[] for _ in range(self.chunk_cols + 1)] 
                        for _ in range(self.chunk_rows + 1)]
        
        self.selected_chunk = None  # Store hovered/selected chunk
        self.add_mode = False
        self.debug_mode = False
        self.add_del = True
        self.controls = True
        
        self.scale_radius = 0  
        self.last_action_time = 0

    def can_act(self, action):
        if action == "debug mode" or action == "CONTROLS": cooldown = 300
        elif action == "add_mode": cooldown = 300
        else: cooldown = 50

        current_time = pg.time.get_ticks()
        if current_time - self.last_action_time >= cooldown:
            self.last_action_time = current_time
            return True
        return False

    def update(self, screen):
        self.update_positions()
        self.draw_boids(screen)

    def draw_boids(self, screen):
        for boid in self.boidlist:
            boid.draw(screen)

    def update_positions(self):
        for row in self.chunks:
            for chunk in row:
                chunk.clear()

        for boid in self.boidlist:
            neighbors = self.get_neighbors(boid)
            centre_mas_ = self.centre_mass(boid, neighbors)
            distancing_ = self.distancing(boid, neighbors)
            match_velo_ = self.match_velocity(boid, neighbors)
            bound_posi_ = self.bound_position(boid)

            boid.velocity = boid.velocity.add(centre_mas_)
            boid.velocity = boid.velocity.add(distancing_)
            boid.velocity = boid.velocity.add(match_velo_)
            boid.velocity = boid.velocity.add(bound_posi_)
            boid.limit_velocity()

            boid.position = boid.position.add(boid.velocity)
            cx, cy = boid.update_chunk()
            if 0 <= cx < self.chunk_cols and 0 <= cy < self.chunk_rows:
                self.chunks[cy][cx].append(boid)
                boid.chunk_coords = (cx, cy)    



    # -----CHUNKS-----
    
    def handle_chunk_edit(self):
        # Gets keys 
        keys = pg.key.get_pressed()
        if keys[pg.K_t] and self.can_act("debug mode"):
            self.debug_mode = not self.debug_mode
        if keys[pg.K_i] and self.can_act("CONTROLS"):
            self.controls = not self.controls

        if self.debug_mode:
            # Mode switching (no cooldown needed, these are toggles)
            if keys[pg.K_s] and self.can_act("add_mode"):
                self.add_mode = not self.add_mode
            if self.add_mode and keys[pg.K_a] and self.can_act("add_mode"):
                self.add_del = not self.add_del
            
            # Gets mouse position
            if self.add_mode:
                mouse_pos = pg.mouse.get_pos()
                center_col = int(mouse_pos[0] // CHUNK_SIZE)
                center_row = int(mouse_pos[1] // CHUNK_SIZE)
                
                # Store selected chunk (center of scale)
                if 0 <= center_row < self.chunk_rows and 0 <= center_col < self.chunk_cols:
                    self.selected_chunk = (center_row, center_col)
                else:
                    self.selected_chunk = None
                
                # Left click = add or delete (use cooldown)
                mouse_buttons = pg.mouse.get_pressed()
                if mouse_buttons[0] and self.selected_chunk:
                    center_row, center_col = self.selected_chunk
                    
                    # Scale mode: loop through square area
                    for row in range(center_row - self.scale_radius, center_row + self.scale_radius + 1):
                        for col in range(center_col - self.scale_radius, center_col + self.scale_radius + 1):
                            if 0 <= row < self.chunk_rows and 0 <= col < self.chunk_cols:
                                self.modify_chunk(row, col)

    def modify_chunk(self, row, col):
        if self.add_del:
            # Add mode: spawn a new boid in this chunk
            new_boid = Boid()
            chunk_center_x = col * CHUNK_SIZE + CHUNK_SIZE // 2
            chunk_center_y = row * CHUNK_SIZE + CHUNK_SIZE // 2
            new_boid.position = Vector2(chunk_center_x, chunk_center_y)
            if len(self.boidlist) < BOID_LIMIT:
                self.boidlist.append(new_boid)
        else:
            # Delete mode: remove all boids in this chunk
            self.boidlist = [
                b for b in self.boidlist
                if not (int(b.position.x // CHUNK_SIZE) == col and 
                        int(b.position.y // CHUNK_SIZE) == row)
            ]
        
    def draw_chunks(self, screen):
        for cy in range(len(self.chunks)):
            for cx in range(len(self.chunks[cy])):
                chunk_x = cx * CHUNK_SIZE
                chunk_y = cy * CHUNK_SIZE
                chunk_rect = (chunk_x, chunk_y, CHUNK_SIZE, CHUNK_SIZE)
                color = CHUNK_EMPTY_COLOR
                width = 1

                if self.debug_mode:
                    # Default colors
                    if len(self.chunks[cy][cx]) == 0:
                        color = CHUNK_EMPTY_COLOR
                    else:
                        color = CHUNK_BOID_COLOR
                    
                    # Check if this chunk is within scale radius of selected chunk
                    is_in_scale_area = False
                    if self.selected_chunk:
                        center_row, center_col = self.selected_chunk
                        if (abs(cy - center_row) <= self.scale_radius and 
                            abs(cx - center_col) <= self.scale_radius):
                            is_in_scale_area = True
                    
                    if self.add_mode:
                        # Highlight selected area
                        if is_in_scale_area:
                            width = 2
                            if not self.add_del:
                                color = CHUNK_SELECTED_DELETE_COLOR  # Light red for delete
                            else:
                                color = CHUNK_SELECTED_ADD_COLOR  # Light green for add
                        # Highlight just the hovered chunk (center)
                        elif self.selected_chunk == (cy, cx):
                            width = 2
                            if not self.add_del:
                                color = CHUNK_SELECTED_DELETE_COLOR  # Bright red
                            else:
                                color = CHUNK_SELECTED_ADD_COLOR  # Bright green
                
                pg.draw.rect(screen, color, chunk_rect, width)

    def draw_hud(self, screen):
        font = pg.font.Font(None, 15)  # Default pygame font, size 24
        
        # Info lines
        debug_status = "ON" if self.debug_mode else "OFF"
        add_mode = "ON" if self.add_mode else "OFF"
        action = "ADD" if self.add_del else "DELETE"
        radius_text = f"Radius: {self.scale_radius}"
        boid_count = f"Boids: {len(self.boidlist)}"
        
        # Build text surface
        lines = [
            f"Debug: {debug_status}",
            f"Add mode {add_mode}", 
            f"Action: {action}",
            f"Selection Radius: {radius_text} chunk(s)",
            f"Boids: {boid_count}"
        ]
        
        # Draw background box and text
        y_offset = 10
        max_width = 0
        
        # First pass: find max width for background box
        for line in lines:
            text_surface = font.render(line, True, (255, 255, 255))
            max_width = max(max_width, text_surface.get_width())

        
        # Draw text
        if self.debug_mode:
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (SCREENWIDTH - text_surface.get_width() - 10, y_offset + i * 25))
        else:
            text_surface = font.render(f"Debug: {debug_status}", True, (255, 255, 255))
            screen.blit(text_surface, (SCREENWIDTH - text_surface.get_width() - 10, y_offset))

    def draw_instructions(self, screen):
        font = pg.font.Font(None, 15)
        lines = [
            "--- CONTROLS ---",
            "T: Toggle Debug Mode",
            "S: Toggle Add Mode (Allows add or delete)",
            "A: Switch Add/Delete Mode (green/red) Only works when Add mode is on",
            "+ / - : Increase/Decrease Scale Radius",
            "Left Click: Add/Delete boids in area",
            "I: Toggle CONTROLS",
            "",
            f"Current Mode: {'ADD' if self.add_del else 'DELETE'}",
            f"Scale Radius: {self.scale_radius} chunk(s)"
        ]
        
        y_offset = 10
        for line in lines:
            text = font.render(line, True, (200, 200, 200))
            screen.blit(text, (10, y_offset))
            y_offset += 18

    # -----BOIDS-----

    # Attempt to move toward the flock's centre mass
    def centre_mass(self, boid, neighbors):
        perceived_center = Vector2(0, 0)
        count = 0  # Count only boids within radius
        
        for adjacent_boid in neighbors:
            if adjacent_boid != boid:
                distance = math.hypot(adjacent_boid.position.x - boid.position.x, adjacent_boid.position.y - boid.position.y)
                if distance <= RECOGNITION_RADIUS: # Only boids that are within recognition distance are taken into account
                    perceived_center = perceived_center.add(adjacent_boid.position) # Add vector to find median later on
                    count += 1
        
        if count > 0:  # Only divide by actual neighbors found
            perceived_center = perceived_center.divide(count) # Finds median
            return perceived_center.subtract(boid.position).divide(200)  # Needs 200 steps to reach median -> prevents teleporting
        return Vector2(0, 0)

    # Distancing + push force amplifies the closer the distance
    def distancing(self, boid, neighbors):
        distancin_ = Vector2(0, 0)
        
        for adjacent_boid in neighbors:
            if adjacent_boid != boid:
                difference = adjacent_boid.position.subtract(boid.position)
                distance = math.hypot(difference.x, difference.y)

                if distance < AVOID_DISTANCE and distance > 0:  # Avoid division by zero
                    # Push away stronger when closer
                    distancin_ = distancin_.subtract(difference.divide(distance * distance))
        
        return distancin_

    # Attempt to match flock's velocity
    def match_velocity(self, boid, neighbors):
        perceived_velocity = Vector2(0, 0)
        count = 0
        
        for adjacent_boid in neighbors:
            if adjacent_boid != boid:
                distance = math.hypot(adjacent_boid.position.x - boid.position.x, adjacent_boid.position.y - boid.position.y)
                if distance <= RECOGNITION_RADIUS:  # Only boids that are within recognition distance are taken into account
                    perceived_velocity = perceived_velocity.add(adjacent_boid.velocity) # Adds to perceived velocity to find median later on
                    count += 1
        
        if count > 0:
            perceived_velocity = perceived_velocity.divide(count) # Medium velocity
            return perceived_velocity.subtract(boid.velocity).divide(20) # Takes 20 steps to reach medium velocity, prevents coke-like behavior
        return Vector2(0, 0) # Prevents division by 0
    
    # Prevent getting out of bound by steering
    def bound_position(self, boid):
        v = Vector2(0, 0)
        margin = 50  # How close to edge before turning
        turn_factor = 0.5 # AKA turn step, dont judge my english
        
        if boid.position.x < margin:
            v.x = turn_factor
        elif boid.position.x > SCREENWIDTH - margin:
            v.x = -turn_factor
        
        if boid.position.y < margin:
            v.y = turn_factor
        elif boid.position.y > SCREENHEIGHT - margin:
            v.y = -turn_factor
        
        return v
    
    # Identify flock
    def get_neighbors(self, boid):
        neighbors = []
        chunk_x = int(boid.position.x // CHUNK_SIZE)
        chunk_y = int(boid.position.y // CHUNK_SIZE)
        
        # How many chunks to check in each direction
        chunk_radius = int(RECOGNITION_RADIUS / CHUNK_SIZE) + 1
        
        for dx in range(-chunk_radius, chunk_radius + 1):
            for dy in range(-chunk_radius, chunk_radius + 1):
                check_x = chunk_x + dx
                check_y = chunk_y + dy
                
                if 0 <= check_x < self.chunk_cols and 0 <= check_y < self.chunk_rows:
                    neighbors.extend(self.chunks[check_y][check_x])
        
        return neighbors # Yes
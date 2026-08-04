from Settings import *
import pygame as pg
import pandas as pd
import numpy as np
import math
import random


def load_weights():
    try:
        weights_df = pd.read_csv("weights.csv")

        weights = weights_df[
            ['fitness', 'w_lazer', 'w_border']
        ].values

        if len(weights) == 0:
            raise ValueError

        fitness = weights[:,0]
        genes = weights[:,1:]
        return genes, fitness

    except:
        print("Creating new random weights")
        genes = np.random.uniform(-1, 1, (POPULATION, 2))
        fitness = np.zeros(POPULATION)
        return genes, fitness

def save_stats(generation, best, average):
    data = {
        "generation": [generation],
        "best": [best],
        "average": [average]
    }

    df = pd.DataFrame(data)

    try:
        old_df = pd.read_csv("stats.csv")
        df = pd.concat([old_df, df], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass

    df.to_csv("stats.csv", index=False)

def load_generation():
    try:
        stats = pd.read_csv("stats.csv")
        if len(stats) > 0:
            return int(stats["generation"].iloc[-1])
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass

    return 0

def load_champion():
    try:
        champion_df = pd.read_csv("champion.csv")

        fitness = champion_df["fitness"].iloc[0]

        weights = champion_df[
            ['w_lazer', 'w_border']
        ].values[0]

        print(
            "Loaded champion:",
            fitness,
            weights
        )

        return fitness, weights

    except:
        return -float("inf"), None

def draw_text(screen, text, x, y, size=16):
    font = pg.font.SysFont(None, size)
    surface = font.render(text, True, (255,255,255))
    screen.blit(surface, (x,y))


# SINGLE BOID
class Boid:
    def __init__(self, position, velocity, direction, acceleration, weights = None):
        self.fitness = 0
        self.time_alive = 0
        self.position_x = position[0]
        self.position_y = position[1]

        # Movement variable (Acceleration still unused)
        self.acceleration = acceleration
        self.direction = direction
        self.velocity = velocity

        # Status
        self.alive = True

        # Reward factors
        self.collision_count = 0
        self.survival_time = 0

        # Randomize weights if theres no weight
        if weights is None:
            self.weights = np.random.uniform(-1, 1, 2)
        else:
            self.weights = weights.copy()

    def move(self):
        dx = self.velocity * np.cos(self.direction)
        dy = self.velocity * np.sin(self.direction)
        self.position_x += dx
        self.position_y += dy
        

    # steering based on other factors
    def update(self, lazer_pos, flock):
        steer_x = 0
        steer_y = 0

        # Lazer avoidance
        dx = self.position_x - lazer_pos[0]
        dy = self.position_y - lazer_pos[1]

        lazer_dist = math.hypot(dx, dy)

        if lazer_dist > 0:
            strength = max(0, 1 - lazer_dist/TRIGGER_DIST)
            steer_x += self.weights[0]*dx/lazer_dist*strength
            steer_y += self.weights[0]*dy/lazer_dist*strength

        # Border avoidance
        dx = self.position_x - CENTER[0]
        dy = self.position_y - CENTER[1]

        border_dist = math.hypot(dx, dy)

        if border_dist > BORDER_RADIUS - 20:
            steer_x -= self.weights[1]*dx/border_dist
            steer_y -= self.weights[1]*dy/border_dist

        # Apply steering
        if steer_x != 0 or steer_y != 0:
            target_direction = math.atan2(steer_y, steer_x)

            difference = target_direction - self.direction

            difference = (difference + PI) % (2*PI) - PI

            turn_speed = 0.15

            self.direction += np.clip(
                difference,
                -turn_speed,
                turn_speed
            )


    # Calculate fitness (Prioritizing no collisions) aka calculating rewards
    def calculate_fitness(self):
        self.fitness = self.survival_time*0.5 # New calulation (Removed collision)

    def draw(self, screen):
        if self.alive:
            pg.draw.circle(screen, (225, 225, 225), (self.position_x, self.position_y), BOID_RADIUS)









class Boids:
    def __init__ (self):
        # Load weights before generation
        all_weights, fitness = load_weights()
        self.average_fitness = 0
        self.alive_count = 0
        self.boids = []

        # Generate boids
        for _ in range(POPULATION):
            boid = Boid(
                position = self.random_position(),
                velocity = random.uniform(1, 3),
                direction = random.uniform(0, 2*PI),
                acceleration=0,
                weights = random.choices(
                    all_weights,
                    weights=np.arange(len(all_weights),0,-1)
                )[0]
            )
            self.boids.append(boid)

    def run(self, lazer):
        # Just updating boids
        for boid in self.boids:
            if boid.alive:
                boid.survival_time += 1
                boid.update((lazer.position_x, lazer.position_y), self.boids)
                self.alive_count += 1
                boid.move()

        # Calculate average fitness
        for boid in self.boids:
            boid.calculate_fitness()
            self.average_fitness += boid.fitness
        self.average_fitness /= POPULATION

    def draw(self, screen):
        for boid in self.boids:
            boid.draw(screen)

    def check_lazer(self, lazer):
        for boid in self.boids:
            dist = math.hypot (boid.position_x - lazer.position_x, boid.position_y - lazer.position_y)

            # If touching lazer -> die (Adjusted for better collision realism)
            if dist < LAZER_RADIUS + BOID_RADIUS:
                boid.alive = False

    def check_border(self): # Kill once touched border
        for boid in self.boids:
            dist = math.hypot (boid.position_x - CENTER[0], boid.position_y - CENTER[1])
            if dist > BORDER_RADIUS - BOID_RADIUS:
                boid.alive = False

    def random_position(self):
        while True:
            x = random.uniform(CENTER[0] - BORDER_RADIUS, CENTER[0] + BORDER_RADIUS)
            y = random.uniform(CENTER[1] - BORDER_RADIUS, CENTER[1] + BORDER_RADIUS)

            if  math.hypot(x - CENTER[0], y - CENTER[1]) < BORDER_RADIUS - BOID_RADIUS \
            and math.hypot(x - CENTER[0], y - CENTER[1]) > LAZER_RADIUS + BOID_RADIUS + 10: return (x, y)

        








class Lazer:
    def __init__ (self, direction, velocity):
        self.position_x = CENTER[0]
        self.position_y = CENTER[1]
        self.direction = direction
        self.velocity = velocity

    def update(self):
        self.position_x += self.velocity * np.cos(self.direction)
        self.position_y += self.velocity * np.sin(self.direction)

        dist = math.hypot(self.position_x - CENTER[0], self.position_y - CENTER[1])
        if dist >= BORDER_RADIUS - LAZER_RADIUS:
            normal_angle = math.atan2(self.position_y - CENTER[1], self.position_x - CENTER[0])

            # Reflect angle and randomize
            self.direction = 2*normal_angle - self.direction - math.pi
            self.direction += random.uniform(-PI/8, PI/8)
            self.position_x = CENTER[0] + (BORDER_RADIUS-LAZER_RADIUS) * math.cos(normal_angle)
            self.position_y = CENTER[1] + (BORDER_RADIUS-LAZER_RADIUS) * math.sin(normal_angle)

    def draw(self, screen):
        pg.draw.circle(screen, LAZERCOLOR, (self.position_x, self.position_y), LAZER_RADIUS)









class UselessBoundary:
    def __init__(self):
        self.position = CENTER

    def draw(self, screen):
        pg.draw.circle(screen, WHITE, CENTER, BORDER_RADIUS)
        pg.draw.circle(screen, SCREENCOLOR, CENTER, BORDER_RADIUS-1)









class Arena:
    def __init__(self):
        self.time_alive = 0
        self.generation = load_generation()+1
        self.survivors = 0

        self.best_fitness, self.best_weights = load_champion()

        self.population = Boids()
        self.lazer = Lazer(
            direction=random.uniform(0, 2*PI),
            velocity=5
        )
        self.arena = UselessBoundary()

    def run(self, screen):
        # Update and draws
        self.time_alive += 1
        self.lazer.update()
        self.arena.draw(screen)
        self.lazer.draw(screen)
        self.population.draw(screen)

        self.draw_stats(screen)
        self.population.run(self.lazer)

        self.population.check_border()
        self.population.check_lazer(self.lazer)

        # Check survivors
        if self.is_dead() or self.time_alive > MAX_TIME:
            self.time_alive = 0
            self.new_generation()

    def draw_stats(self, screen):
        alive = sum(
            1 for boid in self.population.boids
            if boid.alive
        )

        current_best = max(
            (boid.fitness for boid in self.population.boids),
            default=0
        )

        draw_text(
            screen,
            f"Generation: {self.generation}",
            10,
            10
        )

        draw_text(
            screen,
            f"Alive: {alive}/{POPULATION}",
            10,
            40
        )

        draw_text(
            screen,
            f"Current best: {current_best:.2f}",
            10,
            70
        )

        draw_text(
            screen,
            f"Champion: {self.best_fitness:.2f}",
            10,
            100
        )

        draw_text(
            screen,
            f"Time: {self.time_alive}/{MAX_TIME}",
            10,
            130
        )

    def is_dead(self):
        for boid in self.population.boids:
            if boid.alive: return False
        return True

    # New generation (Take the fittest)
    def new_generation(self):
        for boid in self.population.boids:
            boid.calculate_fitness()

        # Ranking
        ranked = sorted(
            self.population.boids,
            key=lambda b: b.fitness,
            reverse=True
        )

        archive = []
        old_weights, old_fitness = load_weights()

        # load old good genes
        for gene, fit in zip(old_weights, old_fitness):
            archive.append(
                [fit, *gene]
            )


        # add current generation genes
        for boid in ranked:
            archive.append(
                [boid.fitness, *boid.weights]
            )


        # sort best first
        archive.sort(
            key=lambda x:x[0],
            reverse=True
        )



        seen = set(tuple(gene[1:]) for gene in archive)

        # Breed until full population (no duplicates)
        while len(archive) < POPULATION:
            parent1 = random.choice(archive[:POPULATION//2])[1:]
            parent2 = random.choice(archive[:POPULATION//2])[1:]
            
            child = np.where(
                np.random.random(len(parent1)) < 0.5,
                parent1,
                parent2
            )
            child += np.random.normal(0, 0.2, len(child))
            child = np.clip(child, -1, 1)

            key = tuple(child)

            if key not in seen:
                seen.add(key)
                archive.append([np.mean(old_fitness), *child])


        # Ranked index = 0 - POPULATION
        # Ranked stored values = Boid
        current_champ_fit = ranked[0].fitness
        current_champ_weights = ranked[0].weights
        print(f"fit {current_champ_fit} | Seed {current_champ_weights}")

        if current_champ_fit > self.best_fitness:
            self.best_weights = current_champ_weights.copy()
            self.best_fitness = current_champ_fit
        

        # Sort and only save best genes
        archive.sort(
            key = lambda x:x[0],
            reverse=True
        )
        archive = archive[:POPULATION]






        # Save champ
        pd.DataFrame(
            [[self.best_fitness, *self.best_weights]],
            columns =[
                "fitness",
                "w_lazer",
                "w_border"
            ]
        ).to_csv(
            "champion.csv",
            index = False
        )


        # Save new archive
        pd.DataFrame(
            archive,
            columns=[
                "fitness",
                "w_lazer",
                "w_border"
            ]
        ).to_csv(
            "weights.csv",
            index=False
        )


        # Save logs
        save_stats(self.generation, current_champ_fit, self.population.average_fitness)
        print(f"Generation {self.generation} | Fittest {current_champ_fit} | Average {self.population.average_fitness}")
        


        # New world
        self.population = Boids()
        self.generation += 1

        self.lazer = Lazer(
            direction=random.uniform(0, 2*PI),
            velocity=5
        )

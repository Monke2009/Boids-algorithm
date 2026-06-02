# FLOCKING ALGORITHM

This is my 14th project, called the flocking algorithm or (boids)

# How it works:
- Every boid would try to move toward the center of mass of neighboring boids
- Every boid would try to keep a small distance from other boids- Every boid would try to match the velocity of nearby boids
# Further tweaking:
- Every boid would attempt to move away from the orders once near

In this case, I used a vector to calculate every boid's next move: The boid would consider every determinant (Including Centre mass, Distancing, Match velocity, Avoid borders)

Because the program only updates once all conditions are considered, there will be no jittering

# UPDATE 1.1:
- Added chunk separations (Boids now would only check for boids in chunks within detection radius) -> Reduce complexity from O(boids * boids) to O(boids * neighboring_chunks_boid_count) -> boid limit exceeds 200
- Additional feature: Boids now move more chaotically -> more natural in my opinion. (Found this accidentally).

# UPDATE 1.2 (FINAL):
- Added HUD
- Added Add/Delete boids
- Added Debug mode (when enabled, you can enable Add_boids, and chunks would glow when boids are inside)
- Added Instructions


# How to run:
1. Install pygame: `pip install pygame`
2. Run: `python main.py`

# How to use:
- Read the CONTROLS section on the upper left corner of the screen when running the program

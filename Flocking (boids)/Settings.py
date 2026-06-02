import math

# HELPERS
class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = math.atan2(y, x)

    def add(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def subtract(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def multiply(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def divide(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def divide_vector(self, scalar):
        return Vector2(self.x / scalar.x, self.y / scalar.y)
    
    def in_place_add(self, other):
        self.x += other.x
        self.y += other.y

    def rotate(self, angle):
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )
    
    def length(self):
        return math.hypot(self.x, self.y)
    
    def normalize(self):
        l = self.length()
        if l == 0: return Vector2()
        return Vector2(self.x / l, self.y / l)
    
    def absolute(self):
        return Vector2(abs(self.x), abs(self.y))
    
# SETTINGS FR FR

PI = math.pi
FPS = 60

BOID_LIMIT = 200
MAXSPEED = 5
MINSPEED = 2
BOID_SIZE = 2
AVOID_DISTANCE = 20
RECOGNITION_RADIUS = 50


TILESIZE = 10
CHUNK_SIZE = 50
SELECT_RADIUS_CAP = 1
SCREENWIDTH = 800
SCREENHEIGHT = 600
WHITE = (255, 255, 255)

CHUNK_EMPTY_COLOR = (40, 40, 64)
CHUNK_BOID_COLOR = (96, 96, 163)

CHUNK_SELECTED_DELETE_COLOR = (255, 100, 100)
CHUNK_SELECTED_ADD_COLOR = (57, 227, 159)
SCREENCOLOR = (25, 25, 40)
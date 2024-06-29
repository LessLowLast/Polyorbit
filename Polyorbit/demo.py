import pygame
import math
import os
from pyo import *
import configparser

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lucid Rhythms")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)

# Orbit setup
CENTER = (WIDTH // 2, HEIGHT // 2)
BASE_VELOCITY = 2  # Base linear velocity for all orbits
GLOBAL_SPEED_MULTIPLIER = 1.0

# Pyo server setup
s = Server().boot()
s.start()

class CelestialBody:
    def __init__(self, radius, size, frequency, sound_file=None):
        self.radius = radius
        self.size = size
        self.angle = 0
        self.frequency = frequency
        self.sound_file = sound_file
        if sound_file and os.path.isfile(sound_file):
            self.sound = SfPlayer(sound_file, loop=False)
        else:
            self.sound = Sine(freq=frequency, mul=0.3)
        self.env = Adsr(attack=0.01, decay=size/10, sustain=0, release=0.01, dur=size/10, mul=self.sound.mul)
        self.sound.mul = self.env
        self.sound.out()
        self.last_x = CENTER[0] + radius

    def draw(self, color):
        x = CENTER[0] + int(self.radius * math.cos(math.radians(self.angle)))
        y = CENTER[1] + int(self.radius * math.sin(math.radians(self.angle)))
        pygame.draw.circle(screen, color, (x, y), self.size)

class Planet(CelestialBody):
    def __init__(self, radius, size, frequency, sound_file=None):
        super().__init__(radius, size, frequency, sound_file)
        self.moons = []

    def add_moon(self, moon):
        self.moons.append(moon)

    def update(self):
        super().update()
        for moon in self.moons:
            moon.update(self.angle, self.radius)

    def draw(self):
        super().draw(WHITE)
        for moon in self.moons:
            moon.draw()

class Moon(CelestialBody):
    def __init__(self, planet_radius, distance, size, frequency, sound_file=None):
        super().__init__(distance, size, frequency, sound_file)
        self.planet_radius = planet_radius

    def update(self, planet_angle, planet_radius):
        super().update()
        planet_x = CENTER[0] + int(planet_radius * math.cos(math.radians(planet_angle)))
        planet_y = CENTER[1] + int(planet_radius * math.sin(math.radians(planet_angle)))
        self.last_x = planet_x + int(self.radius * math.cos(math.radians(self.angle)))
        
    def draw(self):
        planet_x = CENTER[0] + int(self.planet_radius * math.cos(math.radians(self.angle)))
        planet_y = CENTER[1] + int(self.planet_radius * math.sin(math.radians(self.angle)))
        x = planet_x + int(self.radius * math.cos(math.radians(self.angle)))
        y = planet_y + int(self.radius * math.sin(math.radians(self.angle)))
        pygame.draw.circle(screen, BLUE, (x, y), self.size)

def load_settings():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    
    planets = []
    total_distance = 0
    
    num_planets = int(config['Global']['NumberOfPlanets'])
    
    for i in range(1, num_planets + 1):
        section = f'Planet{i}'
        size = int(config[section]['Size'])
        frequency = float(config[section]['Frequency'])
        distance = int(config[section]['Distance'])
        sound_file = config[section].get('SoundFile', '').strip()
        num_moons = int(config[section]['NumberOfMoons'])
        
        total_distance += distance
        planet = Planet(total_distance, size, frequency, sound_file if sound_file else None)
        
        for j in range(1, num_moons + 1):
            moon_section = f'Planet{i}Moon{j}'
            moon_size = int(config[moon_section]['Size'])
            moon_frequency = float(config[moon_section]['Frequency'])
            moon_distance = int(config[moon_section]['Distance'])
            moon_sound_file = config[moon_section].get('SoundFile', '').strip()
            
            moon = Moon(total_distance, moon_distance, moon_size, moon_frequency, 
                        moon_sound_file if moon_sound_file else None)
            planet.add_moon(moon)
        
        planets.append(planet)
    
    return planets

planets = load_settings()

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)

    # Draw and update planets and moons
    for planet in planets:
        pygame.draw.circle(screen, PURPLE, CENTER, planet.radius, 1)
        planet.update()
        planet.draw()

    # Draw center
    pygame.draw.circle(screen, WHITE, CENTER, 5)

    pygame.display.flip()
    clock.tick(60)

# Clean up
s.stop()
pygame.quit()

import pygame
import math
import os
from pyo import *
import configparser

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Polyorbit")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Orbit setup
CENTER = (WIDTH // 2, HEIGHT // 2)
GLOBAL_SPEED_MULTIPLIER = 480.0

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
        max_sustain = 5  # Cap the maximum sustain time
        self.env = Adsr(attack=0.01, decay=size/100, sustain=min(size/200, max_sustain), release=1, dur=size/10, mul=self.sound.mul)
        self.sound.mul = self.env
        self.sound.out()
        self.last_x = CENTER[0] + radius

    def update(self):
        self.angle = (self.angle + GLOBAL_SPEED_MULTIPLIER * (1 / self.radius)) % 360
        current_x = CENTER[0] + int(self.radius * math.cos(math.radians(self.angle)))
        if (self.last_x < CENTER[0] and current_x >= CENTER[0]) or (self.last_x > CENTER[0] and current_x <= CENTER[0]):
            self.env.play()
        self.last_x = current_x

    def draw(self, color, zoom_level):
        x = CENTER[0] + int(self.radius * zoom_level * math.cos(math.radians(self.angle)))
        y = CENTER[1] + int(self.radius * zoom_level * math.sin(math.radians(self.angle)))
        pygame.draw.circle(screen, color, (x, y), int(self.size * zoom_level))

class Planet(CelestialBody):
    def __init__(self, radius, size, frequency, sound_file=None):
        super().__init__(radius, size, frequency, sound_file)
        self.moons = []

    def add_moon(self, moon):
        self.moons.append(moon)

    def update(self):
        super().update()
        for moon in self.moons:
            moon.update(self.angle)

    def draw(self, zoom_level):
        super().draw(WHITE, zoom_level)
        for moon in self.moons:
            moon.draw(zoom_level)

class Moon(CelestialBody):
    def __init__(self, planet, distance, size, frequency, sound_file=None):
        super().__init__(distance, size, frequency, sound_file)
        self.planet = planet

    def update(self, planet_angle):
        self.angle = (self.angle + GLOBAL_SPEED_MULTIPLIER * (1 / self.radius)) % 360
        planet_x = CENTER[0] + int(self.planet.radius * math.cos(math.radians(planet_angle)))
        planet_y = CENTER[1] + int(self.planet.radius * math.sin(math.radians(planet_angle)))
        current_x = planet_x + int(self.radius * math.cos(math.radians(self.angle)))
        if (self.last_x < CENTER[0] and current_x >= CENTER[0]) or (self.last_x > CENTER[0] and current_x <= CENTER[0]):
            self.env.play()
        self.last_x = current_x

    def draw(self, zoom_level):
        planet_x = CENTER[0] + int(self.planet.radius * zoom_level * math.cos(math.radians(self.planet.angle)))
        planet_y = CENTER[1] + int(self.planet.radius * zoom_level * math.sin(math.radians(self.planet.angle)))
        x = planet_x + int(self.radius * zoom_level * math.cos(math.radians(self.angle)))
        y = planet_y + int(self.radius * zoom_level * math.sin(math.radians(self.angle)))
        pygame.draw.circle(screen, BLUE, (x, y), int(self.size * zoom_level))

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
            
            moon = Moon(planet, moon_distance, moon_size, moon_frequency, 
                        moon_sound_file if moon_sound_file else None)
            planet.add_moon(moon)
        
        planets.append(planet)
    
    return planets

planets = load_settings()

running = True
clock = pygame.time.Clock()

zoom_level = 1.0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                zoom_level += 0.1
            elif event.button == 5:  # Scroll down
                zoom_level -= 0.1
                if zoom_level < 0.1:
                    zoom_level = 0.1

    screen.fill(BLACK)

    # Draw the middle line
    pygame.draw.line(screen, RED, (CENTER[0], 0), (CENTER[0], HEIGHT), 1)

    # Draw and update planets and moons
    for planet in planets:
        pygame.draw.circle(screen, PURPLE, CENTER, int(planet.radius * zoom_level), 1)
        planet.update()
        planet.draw(zoom_level)

    # Draw center
    pygame.draw.circle(screen, WHITE, CENTER, 5)

    pygame.display.flip()
    clock.tick(60)

# Clean up
s.stop()
pygame.quit()

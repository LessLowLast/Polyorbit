import pygame
import math
import os
from pyo import *
import configparser
import glob
import pygame_gui

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

# Pyo server setup
s = Server().boot()
s.start()

class CelestialBody:
    def __init__(self, radius, size, frequency, eccentricity, orbit_angle, sound_file=None):
        self.radius = radius
        self.size = size
        self.angle = 0
        self.frequency = frequency
        self.eccentricity = eccentricity
        self.orbit_angle = orbit_angle
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
        self.glow = 0  # New attribute for glow effect

    def update(self, speed_multiplier):
        angular_velocity = speed_multiplier * (1 / self.radius)
        self.angle = (self.angle + angular_velocity) % (2 * math.pi)
        current_x = self.calculate_position()[0]
        if (self.last_x < CENTER[0] and current_x >= CENTER[0]) or (self.last_x > CENTER[0] and current_x <= CENTER[0]):
            self.env.play()
            self.glow = 255  # Set glow to max when activated
        self.last_x = current_x
        
        # Fade out glow
        if self.glow > 0:
            self.glow = max(0, self.glow - 10)

    def calculate_position(self):
        r = self.radius * (1 - self.eccentricity**2) / (1 + self.eccentricity * math.cos(self.angle))
        x = CENTER[0] + int(r * math.cos(self.angle + self.orbit_angle))
        y = CENTER[1] + int(r * math.sin(self.angle + self.orbit_angle))
        return x, y

    def draw(self, color, zoom_level):
        x, y = self.calculate_position()
        x = int((x - CENTER[0]) * zoom_level + CENTER[0])
        y = int((y - CENTER[1]) * zoom_level + CENTER[1])
        
        # Draw glow
        if self.glow > 0:
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, self.glow), (x, y), int(max(self.size * zoom_level * 1.5, 1)))
            screen.blit(glow_surface, (0, 0))
        
        # Draw celestial body
        pygame.draw.circle(screen, color, (x, y), int(max(self.size * zoom_level, 1)))

class Planet(CelestialBody):
    def __init__(self, radius, size, frequency, eccentricity, orbit_angle, sound_file=None):
        super().__init__(radius, size, frequency, eccentricity, orbit_angle, sound_file)
        self.moons = []

    def add_moon(self, moon):
        self.moons.append(moon)

    def update(self, speed_multiplier):
        super().update(speed_multiplier)
        for moon in self.moons:
            moon.update(speed_multiplier)

    def draw(self, zoom_level):
        super().draw(WHITE, zoom_level)
        for moon in self.moons:
            moon.draw(zoom_level)

class Moon(CelestialBody):
    def __init__(self, planet, distance, size, frequency, eccentricity, orbit_angle, sound_file=None):
        super().__init__(distance, size, frequency, eccentricity, orbit_angle, sound_file)
        self.planet = planet

    def update(self, speed_multiplier):
        super().update(speed_multiplier)

    def calculate_position(self):
        planet_x, planet_y = self.planet.calculate_position()
        r = self.radius * (1 - self.eccentricity**2) / (1 + self.eccentricity * math.cos(self.angle))
        x = planet_x + int(r * math.cos(self.angle + self.orbit_angle))
        y = planet_y + int(r * math.sin(self.angle + self.orbit_angle))
        return x, y

    def draw(self, zoom_level):
        x, y = self.calculate_position()
        x = int((x - CENTER[0]) * zoom_level + CENTER[0])
        y = int((y - CENTER[1]) * zoom_level + CENTER[1])
        
        # Draw glow
        if self.glow > 0:
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (BLUE[0], BLUE[1], BLUE[2], self.glow), (x, y), int(max(self.size * zoom_level * 1.5, 1)))
            screen.blit(glow_surface, (0, 0))
        
        # Draw moon
        pygame.draw.circle(screen, BLUE, (x, y), int(max(self.size * zoom_level, 1)))

def load_settings(file):
    config = configparser.ConfigParser()
    config.read(file)
    
    planets = []
    
    global_settings = config['Global']
    speed_multiplier = float(global_settings['SpeedMultiplier'])
    elliptical_orbits = global_settings.getboolean('EllipticalOrbits')
    
    num_planets = int(global_settings['NumberOfPlanets'])
    
    for i in range(1, num_planets + 1):
        section = f'Planet{i}'
        size = int(config[section]['Size'])
        frequency = float(config[section]['Frequency'])
        distance = int(config[section]['Distance'])
        eccentricity = float(config[section]['Eccentricity']) if elliptical_orbits else 0.0
        orbit_angle = float(config[section]['OrbitAngle']) if elliptical_orbits else 0.0
        sound_file = config[section].get('SoundFile', '').strip()
        num_moons = int(config[section]['NumberOfMoons'])
        
        planet = Planet(distance, size, frequency, eccentricity, orbit_angle, sound_file if sound_file else None)
        
        for j in range(1, num_moons + 1):
            moon_section = f'Planet{i}Moon{j}'
            moon_size = int(config[moon_section]['Size'])
            moon_frequency = float(config[moon_section]['Frequency'])
            moon_distance = int(config[moon_section]['Distance'])
            moon_eccentricity = float(config[moon_section]['Eccentricity']) if elliptical_orbits else 0.0
            moon_orbit_angle = float(config[moon_section]['OrbitAngle']) if elliptical_orbits else 0.0
            moon_sound_file = config[moon_section].get('SoundFile', '').strip()
            
            moon = Moon(planet, moon_distance, moon_size, moon_frequency, moon_eccentricity, moon_orbit_angle, 
                        moon_sound_file if moon_sound_file else None)
            planet.add_moon(moon)
        
        planets.append(planet)
    
    return planets, speed_multiplier

def start_recording():
    global is_recording, record_start_time, record_counter
    is_recording = True
    record_start_time = pygame.time.get_ticks()
    filename = f"recording_{record_counter}.wav"
    s.recstart(filename)

def stop_recording():
    global is_recording, record_counter
    is_recording = False
    s.recstop()
    record_counter += 1

# Load planets from settings.ini
planets, GLOBAL_SPEED_MULTIPLIER = load_settings('settings.ini')

# GUI setup
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Dropdown for .ini file selection
ini_files = glob.glob('*.ini')
dropdown = pygame_gui.elements.UIDropDownMenu(
    options_list=ini_files,
    starting_option='settings.ini',
    relative_rect=pygame.Rect((10, 10), (200, 30)),
    manager=manager
)

# Button for sound recording
record_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((220, 10), (150, 30)),
    text='Output for Suno',
    manager=manager
)

running = True
clock = pygame.time.Clock()

zoom_level = 1.0
min_zoom = 0.01  # Allows zooming out 100 times
max_zoom = 10.0  # Allows zooming in 10 times

# Recording variables
is_recording = False
record_start_time = 0
record_counter = 0
RECORDING_DURATION = 19000  # 19 seconds in milliseconds

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                zoom_level *= 1.1
                zoom_level = min(zoom_level, max_zoom)
            elif event.button == 5:  # Scroll down
                zoom_level /= 1.1
                zoom_level = max(zoom_level, min_zoom)
        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == dropdown:
                    selected_file = event.text
                    planets, GLOBAL_SPEED_MULTIPLIER = load_settings(selected_file)
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == record_button:
                    if is_recording:
                        stop_recording()
                        record_button.set_text('Output for Suno')
                    else:
                        start_recording()
                        record_button.set_text('Stop Recording')

        manager.process_events(event)

    manager.update(time_delta)

    # Check if recording needs to be stopped and restarted
    if is_recording:
        current_time = pygame.time.get_ticks()
        if current_time - record_start_time >= RECORDING_DURATION:
            stop_recording()
            start_recording()

    screen.fill(BLACK)

    # Draw the middle line
    pygame.draw.line(screen, RED, (CENTER[0], 0), (CENTER[0], HEIGHT), 1)

    # Draw and update planets and moons
    for planet in planets:
        # Draw orbit
        points = []
        for angle in range(0, 360, 5):
            r = planet.radius * (1 - planet.eccentricity**2) / (1 + planet.eccentricity * math.cos(math.radians(angle)))
            x = CENTER[0] + int(r * math.cos(math.radians(angle) + planet.orbit_angle)) * zoom_level
            y = CENTER[1] + int(r * math.sin(math.radians(angle) + planet.orbit_angle)) * zoom_level
            points.append((x, y))
        pygame.draw.lines(screen, PURPLE, True, points, 1)

        planet.update(GLOBAL_SPEED_MULTIPLIER)
        planet.draw(zoom_level)

        # Draw moon orbits
        for moon in planet.moons:
            moon_points = []
            planet_x, planet_y = planet.calculate_position()
            for angle in range(0, 360, 5):
                r = moon.radius * (1 - moon.eccentricity**2) / (1 + moon.eccentricity * math.cos(math.radians(angle)))
                x = planet_x + int(r * math.cos(math.radians(angle) + moon.orbit_angle)) * zoom_level
                y = planet_y + int(r * math.sin(math.radians(angle) + moon.orbit_angle)) * zoom_level
                moon_points.append((x, y))
            pygame.draw.lines(screen, BLUE, True, moon_points, 1)

    # Draw center
    pygame.draw.circle(screen, WHITE, CENTER, 5)

    # Update button color based on recording state
    if is_recording:
        record_button.colours['normal_bg'] = pygame.Color('red')
        record_button.colours['hovered_bg'] = pygame.Color('darkred')
        record_button.colours['active_bg'] = pygame.Color('darkred')
    else:
        record_button.colours['normal_bg'] = pygame.Color('#45494e')
        record_button.colours['hovered_bg'] = pygame.Color('#35393e')
        record_button.colours['active_bg'] = pygame.Color('#35393e')
    record_button.rebuild()

    manager.draw_ui(screen)

    pygame.display.flip()

# Clean up
s.stop()
pygame.quit()

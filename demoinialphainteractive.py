import pygame
import math
import os
from pyo import *
import configparser
import glob
import pygame_gui
import random
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIHorizontalSlider

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

# Scales
SCALES = {
    "C Major": [131, 147, 165, 175, 196, 220, 247, 261, 293, 329, 349, 392, 440, 493, 523, 587, 659, 698, 784, 880, 987],
    "C Natural Minor": [131, 147, 156, 175, 196, 208, 247, 261, 293, 311, 349, 392, 415, 493, 523, 587, 622, 698, 784, 831, 987],
    "C Harmonic Minor": [131, 147, 156, 175, 196, 208, 247, 261, 293, 311, 349, 392, 440, 493, 523, 587, 622, 698, 784, 880, 987],
    "C Melodic Minor": [131, 147, 156, 175, 196, 220, 247, 261, 293, 311, 349, 392, 440, 493, 523, 587, 622, 698, 784, 880, 987],
    "C Blues": [131, 156, 175, 185, 196, 233, 261, 311, 349, 370, 392, 466, 523, 622, 698, 740, 784, 932],
    "C Pentatonic Major": [131, 147, 165, 196, 220, 261, 293, 329, 392, 440, 523, 587, 659, 784, 880],
    "C Pentatonic Minor": [131, 156, 175, 196, 233, 261, 311, 349, 392, 466, 523, 622, 698, 784, 932],
    "C Dorian": [131, 147, 156, 175, 196, 220, 233, 261, 293, 311, 349, 392, 440, 466, 523, 587, 622, 698, 784, 880, 932],
    "C Phrygian": [131, 139, 165, 175, 196, 208, 247, 261, 277, 329, 349, 392, 415, 493, 523, 554, 659, 698, 784, 831, 987],
    "C Lydian": [131, 147, 165, 185, 196, 220, 247, 261, 293, 329, 370, 392, 440, 493, 523, 587, 659, 740, 784, 880, 987],
    "C Mixolydian": [131, 147, 165, 175, 196, 220, 233, 261, 293, 329, 349, 392, 440, 466, 523, 587, 659, 698, 784, 880, 932],
    "C Locrian": [131, 139, 165, 175, 185, 208, 247, 261, 277, 329, 349, 370, 415, 493, 523, 554, 659, 698, 740, 831, 987],
    "C Whole Tone": [131, 147, 165, 185, 208, 233, 261, 293, 329, 370, 415, 466, 523, 587, 659, 740, 831, 932],
    "C Diminished": [131, 147, 156, 175, 185, 208, 220, 247, 261, 293, 311, 349, 370, 415, 440, 493, 523, 587, 622, 698, 740, 831, 880, 987],
    "C Augmented": [131, 147, 165, 185, 208, 233, 261, 293, 329, 370, 415, 466, 523, 587, 659, 740, 831, 932],
    "C Bebop Dominant": [131, 147, 165, 175, 196, 220, 233, 247, 261, 293, 329, 349, 392, 440, 466, 493, 523, 587, 659, 698, 784, 880, 932, 987],
    "C Bebop Major": [131, 147, 165, 175, 196, 208, 220, 247, 261, 293, 329, 349, 392, 415, 440, 493, 523, 587, 659, 698, 784, 831, 880, 987],
    "C Altered": [131, 139, 165, 175, 185, 208, 233, 261, 277, 329, 349, 370, 415, 466, 523, 554, 659, 698, 740, 831, 932],
}

def get_frequency_in_scale(size, is_planet, has_moons, scale):
    scale_frequencies = SCALES[scale]
    
    if is_planet:
        inverted_size = 50 - size
        if has_moons:
            index = inverted_size * (len(scale_frequencies) // 2) // 50
        else:
            index = (inverted_size * (len(scale_frequencies) // 2) // 50) + (len(scale_frequencies) // 4)
    else:
        inverted_size = 15 - size
        index = (inverted_size * (len(scale_frequencies) // 2) // 15) + (len(scale_frequencies) // 2)
    
    return scale_frequencies[min(max(index, 0), len(scale_frequencies) - 1)]

class CelestialBody:
    def __init__(self, radius, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file=None):
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
        self.env = Adsr(attack=0.01, decay=size/100, sustain=min(size/200, sustain_release_time), release=sustain_release_time, dur=size/10, mul=self.sound.mul)
        self.sound.mul = self.env
        self.sound.out()
        self.last_x = CENTER[0] + radius
        self.glow = 0

    def update(self, speed_multiplier):
        angular_velocity = speed_multiplier * (1 / self.radius)
        self.angle = (self.angle + angular_velocity) % (2 * math.pi)
        current_x = self.calculate_position()[0]
        if (self.last_x < CENTER[0] and current_x >= CENTER[0]) or (self.last_x > CENTER[0] and current_x <= CENTER[0]):
            self.env.play()
            self.glow = 255
        self.last_x = current_x
        
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
        
        if self.glow > 0:
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, self.glow), (x, y), int(max(self.size * zoom_level * 1.5, 1)))
            screen.blit(glow_surface, (0, 0))
        
        pygame.draw.circle(screen, color, (x, y), int(max(self.size * zoom_level, 1)))

class Planet(CelestialBody):
    def __init__(self, radius, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file=None):
        super().__init__(radius, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file)
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
    def __init__(self, planet, distance, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file=None):
        super().__init__(distance, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file)
        self.planet = planet

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
        
        if self.glow > 0:
            glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (BLUE[0], BLUE[1], BLUE[2], self.glow), (x, y), int(max(self.size * zoom_level * 1.5, 1)))
            screen.blit(glow_surface, (0, 0))
        
        pygame.draw.circle(screen, BLUE, (x, y), int(max(self.size * zoom_level, 1)))

def load_settings(file, SUSTAIN_RELEASE_TIME):
    config = configparser.ConfigParser()
    config.read(file)
    
    planets = []
    
    global_settings = config['Global']
    speed_multiplier = float(global_settings['SpeedMultiplier'])
    sustain_release_time = float(global_settings.get('SustainReleaseTime', SUSTAIN_RELEASE_TIME))
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
        
        planet = Planet(distance, size, frequency, eccentricity, orbit_angle, sustain_release_time, sound_file if sound_file else None)
        planet.angle = 0  # Reset the starting angle
        
        for j in range(1, num_moons + 1):
            moon_section = f'Planet{i}Moon{j}'
            moon_size = int(config[moon_section]['Size'])
            moon_frequency = float(config[moon_section]['Frequency'])
            moon_distance = int(config[moon_section]['Distance'])
            moon_eccentricity = float(config[moon_section]['Eccentricity']) if elliptical_orbits else 0.0
            moon_orbit_angle = float(config[moon_section]['OrbitAngle']) if elliptical_orbits else 0.0
            moon_sound_file = config[moon_section].get('SoundFile', '').strip()
            
            moon = Moon(planet, moon_distance, moon_size, moon_frequency, moon_eccentricity, moon_orbit_angle, 
                        sustain_release_time, moon_sound_file if moon_sound_file else None)
            moon.angle = 0  # Reset moon starting angle
            planet.add_moon(moon)
        
        planets.append(planet)
    
    return planets, speed_multiplier, sustain_release_time

def open_settings_gui(manager, distance):
    settings_window = pygame_gui.elements.UIWindow(
        pygame.Rect(50, 50, 300, 450),
        manager,
        window_display_title="New Planet Settings"
    )
    
    y_offset = 10
    pygame_gui.elements.UILabel(pygame.Rect(10, y_offset, 280, 30), "Size:", manager=manager, container=settings_window)
    y_offset += 30
    size_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect(10, y_offset, 280, 30), manager=manager, container=settings_window)
    size_entry.set_text("20")  # Default size
    y_offset += 40
    
    pygame_gui.elements.UILabel(pygame.Rect(10, y_offset, 280, 30), f"Distance: {distance}", manager=manager, container=settings_window)
    y_offset += 40
    
    pygame_gui.elements.UILabel(pygame.Rect(10, y_offset, 280, 30), "Eccentricity:", manager=manager, container=settings_window)
    y_offset += 30
    eccentricity_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect(10, y_offset, 280, 30), manager=manager, container=settings_window)
    eccentricity_entry.set_text("0.0")  # Default eccentricity
    y_offset += 40
    
    pygame_gui.elements.UILabel(pygame.Rect(10, y_offset, 280, 30), "Scale:", manager=manager, container=settings_window)
    y_offset += 30
    scale_dropdown = pygame_gui.elements.UIDropDownMenu(list(SCALES.keys()), "C Major", pygame.Rect(10, y_offset, 280, 30), manager=manager, container=settings_window)
    y_offset += 40
    
    pygame_gui.elements.UILabel(pygame.Rect(10, y_offset, 280, 30), "Number of Moons:", manager=manager, container=settings_window)
    y_offset += 30
    moon_count_entry = pygame_gui.elements.UITextEntryLine(pygame.Rect(10, y_offset, 280, 30), manager=manager, container=settings_window)
    moon_count_entry.set_text("0")
    y_offset += 40

    confirm_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(10, y_offset, 280, 30),
        text="Confirm",
        manager=manager,
        container=settings_window
    )
    
    return settings_window, size_entry, eccentricity_entry, scale_dropdown, moon_count_entry, confirm_button

def create_new_orbit(settings, planets, SUSTAIN_RELEASE_TIME):
    size = int(settings['size'])
    distance = int(settings['distance'])
    eccentricity = float(settings['eccentricity'])
    orbit_angle = random.uniform(0, 2 * math.pi)
    scale = settings['scale'][0] if isinstance(settings['scale'], tuple) else settings['scale']
    moon_count = int(settings['moon_count'])

    frequency = get_frequency_in_scale(size, True, moon_count > 0, scale)
    new_planet = Planet(distance, size, frequency, eccentricity, orbit_angle, SUSTAIN_RELEASE_TIME)
    
    if moon_count > 0:
        min_moon_distance = size + 10
        max_moon_distance = min(distance // 2, size + 100)
        
        moon_distances = []
        for i in range(moon_count):
            if i == 0:
                moon_distances.append(random.randint(min_moon_distance, min_moon_distance + (max_moon_distance - min_moon_distance) // moon_count))
            else:
                moon_distances.append(random.randint(moon_distances[-1] + 10, moon_distances[-1] + (max_moon_distance - min_moon_distance) // moon_count))
        
        for moon_distance in moon_distances:
            moon_size = random.randint(1, min(15, size // 2))
            moon_frequency = get_frequency_in_scale(moon_size, False, False, scale)
            moon_eccentricity = random.uniform(0, eccentricity)
            moon_orbit_angle = random.uniform(0, 2 * math.pi)
            new_moon = Moon(new_planet, moon_distance, moon_size, moon_frequency, moon_eccentricity, moon_orbit_angle, SUSTAIN_RELEASE_TIME)
            new_planet.add_moon(new_moon)

    planets.append(new_planet)
    return new_planet

def update_settings_file(filename, planets, GLOBAL_SPEED_MULTIPLIER, elliptical_orbits, SUSTAIN_RELEASE_TIME):
    config = configparser.ConfigParser()
    config['Global'] = {
        'NumberOfPlanets': str(len(planets)),
        'SpeedMultiplier': str(GLOBAL_SPEED_MULTIPLIER),
        'EllipticalOrbits': str(elliptical_orbits).lower(),
        'MaxEccentricity': '0.99',
        'SelectedScale': 'C Major',
        'SustainReleaseTime': str(SUSTAIN_RELEASE_TIME)
    }
    
    for i, planet in enumerate(planets, 1):
        planet_section = f'Planet{i}'
        config[planet_section] = {
            'Size': str(planet.size),
            'Frequency': str(planet.frequency),
            'Distance': str(planet.radius),
            'NumberOfMoons': str(len(planet.moons)),
            'Eccentricity': f"{planet.eccentricity:.4f}",
            'OrbitAngle': f"{planet.orbit_angle:.4f}",
            'SoundFile': ''
        }
        
        for j, moon in enumerate(planet.moons, 1):
            moon_section = f'{planet_section}Moon{j}'
            config[moon_section] = {
                'Size': str(moon.size),
                'Frequency': str(moon.frequency),
                'Distance': str(moon.radius),
                'Eccentricity': f"{moon.eccentricity:.4f}",
                'OrbitAngle': f"{moon.orbit_angle:.4f}",
                'SoundFile': ''
            }
    
    with open(filename, 'w') as configfile:
        config.write(configfile)

def create_adjustments_panel(manager):
    panel = UIPanel(pygame.Rect(WIDTH - 250, 50, 240, 200), 
                    manager=manager)
    
    UILabel(pygame.Rect(10, 10, 220, 30), "Global Speed Multiplier", manager=manager, container=panel)
    speed_slider = UIHorizontalSlider(pygame.Rect(10, 40, 220, 20), 
                                      GLOBAL_SPEED_MULTIPLIER, (0.1, 10.0), manager=manager, container=panel)
    
    UILabel(pygame.Rect(10, 70, 220, 30), "Sustain/Release Time", manager=manager, container=panel)
    sustain_release_slider = UIHorizontalSlider(pygame.Rect(10, 100, 220, 20), 
                                                SUSTAIN_RELEASE_TIME, (0.1, 2.0), manager=manager, container=panel)
    
    return panel, speed_slider, sustain_release_slider

def create_planet_info_popup(manager, planet, planet_index):
    popup = UIPanel(pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 150, 300, 300), 
                    manager=manager)
    
    y_offset = 10
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Planet {planet_index + 1}", manager=manager, container=popup)
    y_offset += 30
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Size: {planet.size}", manager=manager, container=popup)
    y_offset += 30
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Distance: {planet.radius}", manager=manager, container=popup)
    y_offset += 30
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Frequency: {planet.frequency:.2f}", manager=manager, container=popup)
    y_offset += 30
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Eccentricity: {planet.eccentricity:.4f}", manager=manager, container=popup)
    y_offset += 30
    UILabel(pygame.Rect(10, y_offset, 280, 30), f"Number of Moons: {len(planet.moons)}", manager=manager, container=popup)
    y_offset += 40
    
    delete_button = UIButton(pygame.Rect(10, y_offset, 280, 30), 
                             "Delete Planet", 
                             manager=manager, 
                             container=popup)
    
    close_button = UIButton(pygame.Rect(270, 10, 20, 20), 
                            "X", 
                            manager=manager, 
                            container=popup)
    
    return popup, delete_button, close_button

def update_settings_ini(filename, global_speed_multiplier, sustain_release_time):
    config = configparser.ConfigParser()
    config.read(filename)
    
    if 'Global' not in config:
        config['Global'] = {}
    
    config['Global']['SpeedMultiplier'] = str(global_speed_multiplier)
    config['Global']['SustainReleaseTime'] = str(sustain_release_time)
    
    with open(filename, 'w') as configfile:
        config.write(configfile)

def draw_edit_mode_text(screen, time):
    font = pygame.font.Font(None, 36)
    text = font.render("Edit Mode", True, (255, 255, 0))
    alpha = int(127 + 127 * math.sin(time * 5))  # Pulsing effect
    text.set_alpha(alpha)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
    screen.blit(text, text_rect)

# Initialize SUSTAIN_RELEASE_TIME with a default value
SUSTAIN_RELEASE_TIME = 0.5

# Load planets from settings.ini
planets, GLOBAL_SPEED_MULTIPLIER, SUSTAIN_RELEASE_TIME = load_settings('settings.ini', SUSTAIN_RELEASE_TIME)

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

# Add adjustments panel
adjustments_panel, speed_slider, sustain_release_slider = create_adjustments_panel(manager)
speed_slider.set_current_value(GLOBAL_SPEED_MULTIPLIER)
sustain_release_slider.set_current_value(SUSTAIN_RELEASE_TIME)

# Recording variables
is_recording = False
record_start_time = 0
record_counter = 0
RECORDING_DURATION = 19000  # 19 seconds in milliseconds

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

# Global variables
running = True
clock = pygame.Clock()
zoom_level = 1.0
min_zoom = 0.01
max_zoom = 10.0
paused = False
edit_mode = False
adding_orbit = False
new_orbit_settings = None
initial_click_pos = None
selected_planet = None
planet_info_popup = None
delete_button = None
close_button = None
pulse_time = 0

while running:
    time_delta = clock.tick(60) / 1000.0
    pulse_time += time_delta
    
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
            elif event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for i, planet in enumerate(planets):
                    planet_pos = planet.calculate_position()
                    scaled_pos = ((planet_pos[0] - CENTER[0]) * zoom_level + CENTER[0],
                                  (planet_pos[1] - CENTER[1]) * zoom_level + CENTER[1])
                    distance = math.hypot(mouse_pos[0] - scaled_pos[0], mouse_pos[1] - scaled_pos[1])
                    if distance <= planet.size * zoom_level:
                        selected_planet = planet
                        if planet_info_popup:
                            planet_info_popup.kill()
                        planet_info_popup, delete_button, close_button = create_planet_info_popup(manager, planet, i)
                        break
                else:
                    if edit_mode and not adding_orbit:
                        initial_click_pos = event.pos
                        adding_orbit = True
                        distance = int(math.hypot(initial_click_pos[0] - CENTER[0], initial_click_pos[1] - CENTER[1]) / zoom_level)
                        new_orbit_settings, size_entry, eccentricity_entry, scale_dropdown, moon_count_entry, confirm_button = open_settings_gui(manager, distance)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
                edit_mode = paused
                if not edit_mode:
                    adding_orbit = False
                    if new_orbit_settings:
                        new_orbit_settings.kill()
                    update_settings_file('settings.ini', planets, GLOBAL_SPEED_MULTIPLIER, True, SUSTAIN_RELEASE_TIME)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == dropdown:
                selected_file = event.text
                planets, GLOBAL_SPEED_MULTIPLIER, SUSTAIN_RELEASE_TIME = load_settings(selected_file, SUSTAIN_RELEASE_TIME)
                speed_slider.set_current_value(GLOBAL_SPEED_MULTIPLIER)
                sustain_release_slider.set_current_value(SUSTAIN_RELEASE_TIME)
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == record_button:
                if is_recording:
                    stop_recording()
                    record_button.set_text('Output for Suno')
                else:
                    start_recording()
                    record_button.set_text('Stop Recording')
            elif adding_orbit and event.ui_element == confirm_button:
                new_settings = {
                    'size': size_entry.get_text(),
                    'distance': int(math.hypot(initial_click_pos[0] - CENTER[0], initial_click_pos[1] - CENTER[1]) / zoom_level),
                    'eccentricity': eccentricity_entry.get_text(),
                    'scale': scale_dropdown.selected_option,
                    'moon_count': moon_count_entry.get_text()
                }
                new_planet = create_new_orbit(new_settings, planets, SUSTAIN_RELEASE_TIME)
                dx = initial_click_pos[0] - CENTER[0]
                dy = initial_click_pos[1] - CENTER[1]
                new_planet.angle = math.atan2(dy, dx) - new_planet.orbit_angle
                adding_orbit = False
                new_orbit_settings.kill()
            elif delete_button and event.ui_element == delete_button:
                planets.remove(selected_planet)
                if planet_info_popup:
                    planet_info_popup.kill()
                selected_planet = None
                delete_button = None
                close_button = None
                update_settings_file('settings.ini', planets, GLOBAL_SPEED_MULTIPLIER, True, SUSTAIN_RELEASE_TIME)
            elif close_button and event.ui_element == close_button:
                if planet_info_popup:
                    planet_info_popup.kill()
                selected_planet = None
                delete_button = None
                close_button = None
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == speed_slider:
                GLOBAL_SPEED_MULTIPLIER = event.value
            elif event.ui_element == sustain_release_slider:
                SUSTAIN_RELEASE_TIME = event.value
                for planet in planets:
                    planet.env.sustain = min(planet.size/200, SUSTAIN_RELEASE_TIME)
                    planet.env.release = SUSTAIN_RELEASE_TIME
                    for moon in planet.moons:
                        moon.env.sustain = min(moon.size/200, SUSTAIN_RELEASE_TIME)
                        moon.env.release = SUSTAIN_RELEASE_TIME
            update_settings_ini('settings.ini', GLOBAL_SPEED_MULTIPLIER, SUSTAIN_RELEASE_TIME)

        manager.process_events(event)

    manager.update(time_delta)

    if not paused:
        if is_recording:
            current_time = pygame.time.get_ticks()
            if current_time - record_start_time >= RECORDING_DURATION:
                stop_recording()
                start_recording()

    screen.fill(BLACK)

    # Draw the middle line
    pygame.draw.line(screen, RED, (CENTER[0], 0), (CENTER[0], HEIGHT), 1)

    # Draw orbit preview when in edit mode
    if edit_mode and not adding_orbit:
        preview_color = WHITE
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        transformed_x = (mouse_x - CENTER[0]) / zoom_level + CENTER[0]
        transformed_y = (mouse_y - CENTER[1]) / zoom_level + CENTER[1]
        
        vector_x = transformed_x - CENTER[0]
        vector_y = transformed_y - CENTER[1]
        
        preview_radius = math.hypot(vector_x, vector_y)
        
        preview_points = []
        for angle in range(0, 360, 5):
            x = CENTER[0] + preview_radius * math.cos(math.radians(angle))
            y = CENTER[1] + preview_radius * math.sin(math.radians(angle))
            scaled_x = (x - CENTER[0]) * zoom_level + CENTER[0]
            scaled_y = (y - CENTER[1]) * zoom_level + CENTER[1]
            preview_points.append((scaled_x, scaled_y))
        
        pygame.draw.lines(screen, preview_color, True, preview_points, 1)

    # Draw and update planets and moons
    for planet in planets:
        points = []
        for angle in range(0, 360, 5):
            r = planet.radius * (1 - planet.eccentricity**2) / (1 + planet.eccentricity * math.cos(math.radians(angle)))
            x = CENTER[0] + int(r * math.cos(math.radians(angle) + planet.orbit_angle)) * zoom_level
            y = CENTER[1] + int(r * math.sin(math.radians(angle) + planet.orbit_angle)) * zoom_level
            points.append((x, y))
        pygame.draw.lines(screen, PURPLE, True, points, 1)

        if not paused:
            planet.update(GLOBAL_SPEED_MULTIPLIER)
        planet.draw(zoom_level)

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

    # Draw "Edit Mode" text when paused
    if edit_mode:
        draw_edit_mode_text(screen, pulse_time)

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

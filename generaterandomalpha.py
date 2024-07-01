import configparser
import random
import math

# Define scales (3 octaves each where applicable)
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

def get_user_input():
    while True:
        try:
            min_planets = int(input("Enter the minimum number of planets: "))
            max_planets = int(input("Enter the maximum number of planets: "))
            min_moons = int(input("Enter the minimum number of moons per planet: "))
            max_moons = int(input("Enter the maximum number of moons per planet: "))
            min_center_distance = int(input("Enter the minimum distance from center for planets: "))
            min_planet_distance = int(input("Enter the minimum distance from planet for moons: "))
            random_distance = input("Should planet distances be random? (yes/no): ").lower() == 'yes'
            
            if random_distance:
                min_planet_separation = int(input("Enter the minimum separation between planets: "))
            else:
                fixed_planet_separation = int(input("Enter the fixed distance between planets: "))
            
            speed_multiplier = float(input("Enter the global speed multiplier (e.g., 480.0): "))
            elliptical_orbits = input("Enable elliptical orbits? (yes/no): ").lower() == 'yes'
            
            if elliptical_orbits:
                max_eccentricity = float(input("Enter the maximum eccentricity (0.0-0.99): "))
                if max_eccentricity < 0.0 or max_eccentricity >= 1.0:
                    print("Eccentricity must be between 0.0 and 0.99.")
                    continue
            else:
                max_eccentricity = 0.0
            
            print("\nAvailable scales:")
            for i, scale in enumerate(SCALES.keys(), 1):
                print(f"{i}. {scale}")
            
            while True:
                try:
                    scale_choice = int(input("Select a scale (enter the number): ")) - 1
                    if 0 <= scale_choice < len(SCALES):
                        selected_scale = list(SCALES.keys())[scale_choice]
                        break
                    else:
                        print("Invalid selection. Please choose a number from the list.")
                except ValueError:
                    print("Please enter a valid number.")
            
            if (min_planets <= 0 or max_planets <= 0 or min_planets > max_planets or
                min_moons < 0 or max_moons < 0 or min_moons > max_moons or
                min_center_distance < 0 or min_planet_distance < 0 or speed_multiplier <= 0):
                print("Invalid input. Please ensure all values are non-negative and logical.")
                continue
            
            return (min_planets, max_planets, min_moons, max_moons, min_center_distance, 
                    min_planet_distance, random_distance, 
                    min_planet_separation if random_distance else fixed_planet_separation,
                    speed_multiplier, elliptical_orbits, max_eccentricity, selected_scale)
        except ValueError:
            print("Please enter valid values.")

def get_frequency_in_key(size, is_planet, has_moons, scale):
    scale_frequencies = SCALES[scale]
    
    if is_planet:
        inverted_size = 50 - size + 20
        if has_moons:
            index = (inverted_size - 20) * 14 // 30
        else:
            index = ((inverted_size - 20) * 14 // 30) + 7
        return scale_frequencies[min(max(index, 0), len(scale_frequencies) - 1)]
    else:
        inverted_size = 16 - size
        index = ((inverted_size - 1) * 7 // 14) + 14
        return scale_frequencies[min(max(index, 14), len(scale_frequencies) - 1)]

def generate_random_settings(file_name='settings.ini'):
    (min_planets, max_planets, min_moons, max_moons, min_center_distance, 
     min_planet_distance, random_distance, distance_parameter,
     speed_multiplier, elliptical_orbits, max_eccentricity, selected_scale) = get_user_input()
    
    config = configparser.ConfigParser()
    
    num_planets = random.randint(min_planets, max_planets)
    config['Global'] = {
        'NumberOfPlanets': str(num_planets),
        'SpeedMultiplier': str(speed_multiplier),
        'EllipticalOrbits': str(elliptical_orbits).lower(),
        'MaxEccentricity': str(max_eccentricity),
        'SelectedScale': selected_scale
    }

    previous_planet_distance = min_center_distance
    for i in range(1, num_planets + 1):
        planet_section = f'Planet{i}'
        size = random.randint(20, 50)
        num_moons = random.randint(min_moons, max_moons)
        has_moons = num_moons > 0
        frequency = get_frequency_in_key(size, True, has_moons, selected_scale)
        
        if random_distance:
            distance = previous_planet_distance + random.randint(distance_parameter, distance_parameter + 50)
        else:
            distance = previous_planet_distance + distance_parameter
        
        previous_planet_distance = distance
        sound_file = ""

        eccentricity = random.uniform(0, max_eccentricity) if elliptical_orbits else 0.0
        orbit_angle = random.uniform(0, 2 * math.pi) if elliptical_orbits else 0.0

        config[planet_section] = {
            'Size': str(size),
            'Frequency': str(frequency),
            'Distance': str(distance),
            'NumberOfMoons': str(num_moons),
            'SoundFile': sound_file,
            'Eccentricity': f"{eccentricity:.4f}",
            'OrbitAngle': f"{orbit_angle:.4f}"
        }

        previous_moon_distance = min_planet_distance
        for j in range(1, num_moons + 1):
            moon_section = f'{planet_section}Moon{j}'
            moon_size = random.randint(1, 15)
            moon_frequency = get_frequency_in_key(moon_size, False, True, selected_scale)
            moon_distance = previous_moon_distance + random.randint(moon_size, 20)
            previous_moon_distance = moon_distance
            moon_sound_file = ""

            moon_eccentricity = random.uniform(0, max_eccentricity) if elliptical_orbits else 0.0
            moon_orbit_angle = random.uniform(0, 2 * math.pi) if elliptical_orbits else 0.0

            config[moon_section] = {
                'Size': str(moon_size),
                'Frequency': str(moon_frequency),
                'Distance': str(moon_distance),
                'SoundFile': moon_sound_file,
                'Eccentricity': f"{moon_eccentricity:.4f}",
                'OrbitAngle': f"{moon_orbit_angle:.4f}"
            }

    with open(file_name, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    generate_random_settings()
    print("Random settings.ini file has been generated.")

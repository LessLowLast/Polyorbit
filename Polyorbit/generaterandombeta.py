import configparser
import random

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
            
            if (min_planets <= 0 or max_planets <= 0 or min_planets > max_planets or
                min_moons < 0 or max_moons < 0 or min_moons > max_moons or
                min_center_distance < 0 or min_planet_distance < 0):
                print("Invalid input. Please ensure all values are non-negative and logical.")
                continue
            
            return (min_planets, max_planets, min_moons, max_moons, min_center_distance, 
                    min_planet_distance, random_distance, 
                    min_planet_separation if random_distance else fixed_planet_separation)
        except ValueError:
            print("Please enter valid integer values.")

def get_frequency_in_key(size, is_planet, has_moons=True):
    # C major scale frequencies (3 octaves)
    c_major_scale = [
        131, 147, 165, 175, 196, 220, 247,  # Lower octave
        261, 293, 329, 349, 392, 440, 493,  # Middle octave
        523, 587, 659, 698, 784, 880, 987   # Higher octave
    ]
    
    if is_planet:
        # Invert the size so that larger planets have lower frequencies
        inverted_size = 50 - size + 20  # This maps 20-50 to 50-20
        
        if has_moons:
            # For planets with moons: use lower to middle octaves
            index = (inverted_size - 20) * 14 // 30  # Maps 50-20 to 0-14
        else:
            # For planets without moons: use middle to higher octaves
            index = ((inverted_size - 20) * 14 // 30) + 7  # Maps 50-20 to 7-21
        
        return c_major_scale[min(max(index, 0), len(c_major_scale) - 1)]
    else:
        # For moons: size range 1-15, use higher octaves
        # Invert the size for moons as well
        inverted_size = 16 - size  # This maps 1-15 to 15-1
        index = ((inverted_size - 1) * 7 // 14) + 14  # Maps 15-1 to 14-21
        return c_major_scale[min(max(index, 14), len(c_major_scale) - 1)]

def generate_random_settings(file_name='settings.ini'):
    (min_planets, max_planets, min_moons, max_moons, min_center_distance, 
     min_planet_distance, random_distance, distance_parameter) = get_user_input()
    
    config = configparser.ConfigParser()
    
    # Global settings
    num_planets = random.randint(min_planets, max_planets)
    config['Global'] = {'NumberOfPlanets': str(num_planets)}

    previous_planet_distance = min_center_distance
    for i in range(1, num_planets + 1):
        planet_section = f'Planet{i}'
        size = random.randint(20, 50)
        num_moons = random.randint(min_moons, max_moons)
        has_moons = num_moons > 0
        frequency = get_frequency_in_key(size, True, has_moons)
        
        if random_distance:
            distance = previous_planet_distance + random.randint(distance_parameter, distance_parameter + 50)
        else:
            distance = previous_planet_distance + distance_parameter
        
        previous_planet_distance = distance
        sound_file = ""

        config[planet_section] = {
            'Size': str(size),
            'Frequency': str(frequency),
            'Distance': str(distance),
            'NumberOfMoons': str(num_moons),
            'SoundFile': sound_file
        }

        previous_moon_distance = min_planet_distance
        for j in range(1, num_moons + 1):
            moon_section = f'{planet_section}Moon{j}'
            moon_size = random.randint(1, 15)
            moon_frequency = get_frequency_in_key(moon_size, False)
            moon_distance = previous_moon_distance + random.randint(moon_size, 20)
            previous_moon_distance = moon_distance
            moon_sound_file = ""

            config[moon_section] = {
                'Size': str(moon_size),
                'Frequency': str(moon_frequency),
                'Distance': str(moon_distance),
                'SoundFile': moon_sound_file
            }

    with open(file_name, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    generate_random_settings()
    print("Random settings.ini file has been generated.")

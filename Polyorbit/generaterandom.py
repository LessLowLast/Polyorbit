import configparser
import random

def get_user_input():
    while True:
        try:
            min_planets = int(input("Enter the minimum number of planets: "))
            max_planets = int(input("Enter the maximum number of planets: "))
            min_moons = int(input("Enter the minimum number of moons per planet: "))
            max_moons = int(input("Enter the maximum number of moons per planet: "))
            
            if (min_planets <= 0 or max_planets <= 0 or min_planets > max_planets or
                min_moons < 0 or max_moons < 0 or min_moons > max_moons):
                print("Invalid input. Please ensure:")
                print("- Minimum planets is positive and not greater than maximum planets")
                print("- Minimum moons is non-negative and not greater than maximum moons")
                continue
            return min_planets, max_planets, min_moons, max_moons
        except ValueError:
            print("Please enter valid integer values.")

def calculate_frequency(size, is_planet):
    if is_planet:
        # For planets: size range 20-50, frequency range 50-600
        return 600 - ((size - 20) / 30) * 550
    else:
        # For moons: size range 1-15, frequency range 100-800
        return 800 - ((size - 1) / 14) * 700

def generate_random_settings(file_name='settings.ini'):
    min_planets, max_planets, min_moons, max_moons = get_user_input()
    
    config = configparser.ConfigParser()
    
    # Global settings
    num_planets = random.randint(min_planets, max_planets)
    config['Global'] = {'NumberOfPlanets': str(num_planets)}

    previous_planet_distance = 0
    for i in range(1, num_planets + 1):
        planet_section = f'Planet{i}'
        size = random.randint(20, 50)  # Planets have a minimum size of 20
        frequency = calculate_frequency(size, True)
        distance = previous_planet_distance + random.randint(50, 100)
        previous_planet_distance = distance
        num_moons = random.randint(min_moons, max_moons)
        sound_file = ""

        config[planet_section] = {
            'Size': str(size),
            'Frequency': f"{frequency:.2f}",
            'Distance': str(distance),
            'NumberOfMoons': str(num_moons),
            'SoundFile': sound_file
        }

        previous_moon_distance = size
        for j in range(1, num_moons + 1):
            moon_section = f'{planet_section}Moon{j}'
            moon_size = random.randint(1, 15)  # Moons have a maximum size of 15
            moon_frequency = calculate_frequency(moon_size, False)
            moon_distance = previous_moon_distance + random.randint(moon_size, 20)
            previous_moon_distance = moon_distance
            moon_sound_file = ""

            config[moon_section] = {
                'Size': str(moon_size),
                'Frequency': f"{moon_frequency:.2f}",
                'Distance': str(moon_distance),
                'SoundFile': moon_sound_file
            }

    with open(file_name, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    generate_random_settings()
    print("Random settings.ini file has been generated.")

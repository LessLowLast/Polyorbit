# Polyorbit
Make planets, make moons, set distance to set orbit, when moons or planets pass the middle line, they play a sound. Polyrhythm 

Clone anywhere or download the polyorbit folder, or, just download demoini.py and generaterandom.py and put them in a folder somewhere.

1. pip install pygame pyo
2. Run generaterandom.py
3. Edit the settings file if you want.
4. Run demoini.py

generaterandombeta has some more features, and for now is locked to CMajor for frequencies to produce some better sounding overall sound with lots of moons and planets. 

I plan on forcing in a scale selection option soon so it can also only pull from certain scales for sounds. Interesting stuff.


To run the beta, you only need the beta generator found in the PolyOrbit folder. 

To run the alpha, which includes elliptical orbit generation, and a speed mult (1-5, the base speed is 480, this is a multiplier to that number), you need both demoinialpha, and generaterandomalpha.py from the root. the commands should be appropriately replaced.

For the newest alpha you will also need to run...

pip install pygame_gui

... or it probably wont launch. 

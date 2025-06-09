# Import packages
import multiprocessing as mp                    # For multiprocessing
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"

# Enter number of frames to be animated, define as None for all files
bulkfile_number = 10

animations = [("2D", "B_tot","anim1.gif"),("2D", "v_y","anim2.gif")]

for object in animations:
    object = AnimationSpecs(
            object[0], object[1], object[2], bulkpath, bulkfile_number)

def main():
    with mp.Pool(len(animations)) as process:
        process.map(AnimationEngine, animations)

if __name__ == "__main__":
    main()
# Import packages
import multiprocessing as mp                    # For multiprocessing
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"

# Enter number of frames to be animated, define as None for all files
bulkfile_number = 200

animations = [("2D", "rho","sim15_rho_2D.gif"),("3D", "rho","sim15_rho_3D.gif")]

for i, object in enumerate(animations):
    animations[i] = AnimationSpecs(object[0], object[1], object[2], bulkpath, bulkfile_number)


with mp.Pool(len(animations)) as process:
    process.map(AnimationEngine, animations)
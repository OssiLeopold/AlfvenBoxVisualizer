# Import packages
import multiprocessing as mp                    # For multiprocessing
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"

# Enter number of frames to be animated, define as None for all files
bulkfile_number = 10

# Define what animations are to be produced
# Has to be in the from of a tuple, e.g: ("<animation type>", "<variable_component>", "<dir/outputname.gif>")
# animation types: 2D, 3D
# variable_component: B_y, B_z, B_tot, <same for v>, and rho (for proton density)
animations = [("2D", "rho","sim15_rho_2D.gif"),("3D", "rho","sim15_rho_3D.gif")]

# Turn list into list of AnimationSpecs objects
for i, object in enumerate(animations):
    animations[i] = AnimationSpecs(object[0], object[1], object[2], bulkpath, bulkfile_number)

# Launch a separate process for each AnimationSpecs object
with mp.Pool(len(animations)) as process:
    process.map(AnimationEngine, animations)
# Import packages
import multiprocessing as mp                    # For multiprocessing
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim7/"

# Enter number of frames to be animated, define as None for all files
bulkfile_number = 10

# Define what animations are to be produced
# Has to be in the from of a tuple, e.g: ("<animation type>", "<variable_component>")
# animation types: 2D, 3D
# variable_component: B_y, B_z, B_tot, <same for v>, and rho (for proton density)
def_beginning = "TurbulenceBoxPlots/sim7_plots/sim7"
def_end = ".mp4"
animations = [("fourier", "B_x"),("fourier", "B_y"),("fourier", "B_z"),("fourier", "B_tot")]

""" ("2D", "v_x"),("2D", "v_y"),("2D", "v_z"),("2D", "v_tot"),
              ("3D", "v_x"),("3D", "v_y"),("3D", "v_z"),("3D", "v_tot"),
              ("2D", "B_x"),("2D", "B_y"),("2D", "B_z"),("2D", "B_tot"),
              ("3D", "B_x"),("3D", "B_y"),("3D", "B_z"),("3D", "B_tot") """

""" ("2D", "v_y"),("2D", "v_z"),("2D", "v_tot"),
              ("3D", "v_y"),("3D", "v_z"),("3D", "v_tot"),
              ("2D", "J_y"),("2D", "J_y"),("3D", "J_y"),("3D", "J_z"),
              ("fourier", "B_y"),("fourier", "B_z") """

# Turn list into list of AnimationSpecs objects
for i, object in enumerate(animations):
    animations[i] = AnimationSpecs(object[0], object[1], f"{def_beginning}_{object[1]}_{object[0]}{def_end}", bulkpath, bulkfile_number)

# Launch a separate process for each AnimationSpecs object
with mp.Pool(len(animations)) as process:
    process.map(AnimationEngine, animations)

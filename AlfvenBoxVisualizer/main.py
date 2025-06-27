# Import packages
import multiprocessing as mp                    # For multiprocessing
import sys, os
from multiprocessing import shared_memory
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation
import analysator as pt
import numpy as np

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks_local/sim21/"

# Enter number of frames to be animated. Define start frame if you want to start from some point.
bulkfile_number = 1
start_frame = 0

# Please enter guide field strength and direction
G_field = ("z", 1e-8)

# Define what animations are to be produced
# Has to be in the from of a tuple, e.g: ("<animation type>", "<variable_component>", "<fourier spesific>")
# animation types: 2D, 3D, fourier,
# variable_component: B_y, B_z, B_tot, <same for v>, and rho (for proton density)
# fourier_spesific: ("x", <0-1>) -> x (or y) states the direction along which you want the slice to be done.
#                   <0-1> states the y (or x) coordinate where you want the slice to be done (0-1 -> y_min - y_max).
# fourier_spesific: ("diag", <1 or 2>) -> if you want fourier in diagonal direction. Enter 1 if you want SW-NE.
#                   Enter 2 if you want NW-SW.
# fourier_spesific: ("trace", <0-1>, <0-1>) -> If you want trace PSD.
#                   First number for x slice y-coord and second number for y slice x-coord.
# fourier_spesific: ("trace_diag") -> for trace PSD for diag directions.
 
def_beginning = "TurbulenceBoxPlots/sim22_anim/sim22"
def_end = ".mp4"
animations = [
              ("2D", "B_x"),("2D", "B_y"),("2D", "B_z"),("2D", "B_tot")
             ]

""" ("fourier", "v_x", ("x","0.5")),("fourier", "v_y", ("x","0.5")),("fourier", "v_z", ("x","0.5")),("fourier", "B_x", ("x","0.5")),("fourier", "B_y", ("x","0.5")),("fourier", "B_z", ("x","0.5")),
              ("fourier", "v_x", ("trace_diag")),("fourier", "v_y", ("trace_diag")),("fourier", "v_z", ("trace_diag")),("fourier", "B_x", ("trace_diag")),("fourier", "B_y", ("trace_diag")),("fourier", "B_z", ("trace_diag")) """

""" ("fourier", "B_x"),("fourier", "B_y"),("fourier", "B_z") """

""" ("2D", "B_x"),("2D", "B_y"),("2D", "B_z"),("2D", "B_tot"),
              ("2D", "v_x"),("2D", "v_y"),("2D", "v_z"),("2D", "v_tot"),
              ("2D", "J_x"),("2D", "J_y"),("2D", "J_z"), """


# Turn list into list of AnimationSpecs objects

for i, object in enumerate(animations):
    if object[0] == "fourier":
        animations[i] = AnimationSpecs(object[0], object[1], f"{def_beginning}_{object[1]}_{object[0]}_{object[2][0]}_{def_end}", bulkfile_number, start_frame, bulkpath, object[2], G_field)
    else:
        animations[i] = AnimationSpecs(object[0], object[1], f"{def_beginning}_{object[1]}_{object[0]}{def_end}", bulkfile_number, start_frame, bulkpath, "pass", G_field)


# Launch a separate process for each AnimationSpecs object
with mp.Pool(len(animations)) as process:
    process.map(AnimationEngine, animations)


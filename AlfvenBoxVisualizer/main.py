# Import packages
import multiprocessing as mp                    # For multiprocessing
from animation_specs import AnimationSpecs      # Class for animation object
from animation_engine import AnimationEngine    # Class for doing actual animation

# Set path to simulation bulkfiles
bulkpath = "/home/rxelmer/Documents/turso/bulks_local/sim16/"

# Enter number of frames to be animated, define as None for all files
bulkfile_number = 10

# Define what animations are to be produced
# Has to be in the from of a tuple, e.g: ("<animation type>", "<variable_component>", "<dir/outputname.gif>")
# animation types: 2D, 3D
# variable_component: B_y, B_z, B_tot, <same for v>, and rho (for proton density)
animations = [ ("2D", "B_x", "sim16_plots/sim16_Bx_2D.gif"),("2D", "B_y", "sim16_plots/sim16_By_2D.gif"),
                ("2D", "B_z", "sim16_plots/sim16_Bz_2D.gif"),("2D", "v_x", "sim16_plots/sim16_vx_2D.gif"),
                ("2D", "v_y", "sim16_plots/sim16_vy_2D.gif"),("2D", "v_z", "sim16_plots/sim16_vz_2D.gif"),
                ("3D", "B_x", "sim16_plots/sim16_Bx_3D.gif"),("3D", "B_y", "sim16_plots/sim16_By_3D.gif"),
                ("3D", "B_z", "sim16_plots/sim16_Bz_3D.gif"),("3D", "v_x", "sim16_plots/sim16_vx_3D.gif"),
                ("3D", "v_y", "sim16_plots/sim16_vy_3D.gif"),("3D", "v_z", "sim16_plots/sim16_vz_3D.gif"),

                ("2D", "B_tot", "sim16_plots/sim16_B_tot_2D.gif"),("2D", "v_tot", "sim16_plots/sim16_v_tot_2D.gif"),
                ("3D", "B_tot", "sim16_plots/sim16_B_tot_3D.gif"),("3D", "v_tot", "sim16_plots/sim16_v_tot_3D.gif"),
                ("2D", "dB_y/dx", "sim16_plots/sim16_dBy_dx_2D.gif"),("2D", "dB_z/dx", "sim16_plots/sim16_dBz_dx_2D.gif"),
                ("3D", "dB_y/dx", "sim16_plots/sim16_dBy_dx_3D.gif"),("3D", "dB_z/dx", "sim16_plots/sim16_dBz_dx_3D.gif"),
                ("2D", "J_y", "sim16_plots/sim16_Jy_2D.gif"),("2D", "J_z", "sim16_plots/sim16_Jz_2D.gif"),
                ("3D", "J_y", "sim16_plots/sim16_Jy_3D.gif"),("3D", "J_z", "sim16_plots/sim16_Jz_3D.gif")]

# Turn list into list of AnimationSpecs objects
for i, object in enumerate(animations):
    animations[i] = AnimationSpecs(object[0], object[1], object[2], bulkpath, bulkfile_number)

# Launch a separate process for each AnimationSpecs object
with mp.Pool(len(animations)) as process:
    process.map(AnimationEngine, animations)
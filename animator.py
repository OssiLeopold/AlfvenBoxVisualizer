import numpy as np                  # For math
import matplotlib.pyplot as plt     # For plotting
import analysator as pt             # For manipulating .vlsv files
# Packages for gif animation
from matplotlib.animation import PillowWriter
import matplotlib.animation as animation

def animatorFunc(animation):
    vobj = pt.vlsvfile.VlsvReader(animation.bulkpath + "bulk.0000000.vlsv")
    r_e = 6371e3 # Earth radius
    x_length = vobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
    xmax = vobj.read_parameter("xmax")/r_e # For now only used for placement of time legend
    ymax = vobj.read_parameter("ymax")/r_e # For now only used for placement of time legend

    cellids = vobj.read_variable("CellID")
    x = np.array([vobj.get_cell_coordinates(c)[0] for c in np.sort(cellids)])/r_e
    x_mesh = x.reshape(-1,x_length)
    y = np.array([vobj.get_cell_coordinates(c)[1] for c in np.sort(cellids)])/r_e
    y_mesh = y.reshape(-1,x_length)
    colors = ["blue", "orange"]
    
    if animation.animation_type == "2D":
        fig = plt.figure()
        ax = fig.add_subplot()

        if animation.component == "total":
            Min = 0
            Max = 1.5 * max(vobj.read_variable(animation.variable,operator="y"))/animation.unit
        else:
            Min = min(vobj.read_variable(animation.variable,operator=animation.component))/animation.unit
            Max = max(vobj.read_variable(animation.variable,operator=animation.component))/animation.unit

        levels = 100                                                          # How many color levels will be drawn, choose less if you want quicker animation
        level_boundaries = np.linspace(Min, Max, levels + 1)                  # Used to fix colorbar to a certain range

        p = []
        if animation.component == "total":
            y_component = np.array(vobj.read_variable(animation.variable,operator="y")[cellids.argsort()])/animation.unit
            z_component = np.array(vobj.read_variable(animation.variable,operator="z")[cellids.argsort()])/animation.unit
            total = np.sqrt(y_component**2 + z_component**2)
            total_mesh = total.reshape(-1, x_length)
            p.append(ax.contourf(x_mesh, y_mesh, total_mesh, level_boundaries))

        plt.savefig(f"ffff{animation.unit}.png")

    else:
        print("gukki")
import os
import analysator as pt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
#enabling use of latex
os.environ['PATH']='/home/rxelmer/Documents/turso/appl_local/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] 
os.environ['PTNOLATEX']='1'

R_E = 6371e3 # Earth radius
COLORS = ["blue", "orange"]

class AnimationEngine:
    def __init__(self, object):
        self.object = object

        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + "bulk.0000000.vlsv")
        self.cellids = vlsvobj.read_variable("CellID") # Used for sorting variables read by VlsvReader
        self.x_length = vlsvobj.read_parameter("xcells_ini") # Used for formatting numpy mesh
        self.xmax = vlsvobj.read_parameter("xmax") / R_E
        self.ymax = vlsvobj.read_parameter("ymax") / R_E

        # Used in plotting
        x = np.array([vlsvobj.get_cell_coordinates(coord)[0] for coord in np.sort(self.cellids)]) / R_E
        y = np.array([vlsvobj.get_cell_coordinates(coord)[1] for coord in np.sort(self.cellids)]) / R_E
        self.x_mesh = x.reshape(-1,self.x_length)
        self.y_mesh = y.reshape(-1,self.x_length)
        
        # Bring to class scope
        self.vlsvobj = vlsvobj
        self.cid_sort = self.cellids.argsort()

        if object.animation_type == "2D":
            self.animation_2D()

        elif object.animation_type == "3D":
            self.animation_3D()

    def animation_2D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cid_sort = self.cid_sort

        fig = plt.figure()
        ax = fig.add_subplot()

        if object.component == "total":
            Min = 0
            Max = self.def_min_max()
        else:
            Min, Max = self.def_min_max()

        levels = 100
        if object.variable == "vg_b_vol" and object.component == "x":
            level_boundaries = np.linspace(Min*0.9, Max*1.1, levels + 1)
        else:
            level_boundaries = np.linspace(Min, Max, levels + 1)
        self.level_boundaries = level_boundaries

        p = []
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            p.append(ax.contourf(self.x_mesh, self.y_mesh, magnitude_mesh, level_boundaries))
        elif object.component == "deriv":
            value = np.array(vlsvobj.read_variable(object.variable)[cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            p.append(ax.contourf(self.x_mesh, self.y_mesh, value_mesh, level_boundaries))
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            p.append(ax.contourf(self.x_mesh, self.y_mesh, value_mesh, level_boundaries))
        
        self.p = p
        self.ax = ax

        cbar = plt.colorbar(p[0])
        if object.variable == "vg_b_vol":
            cbar.set_label(f"B_{object.component} [nT]")
            ax.set_title(f"B_{object.component} [nT]")
        elif object.variable == "proton/vg_v":
            cbar.set_label(f"v_{object.component} [km/s]")
            ax.set_title(f"v_{object.component} [km/s]")
        elif object.variable == "proton/vg_rho":
            cbar.set_label(("rho [1e6/cell]"))
            ax.set_title(f"rho [1e6/cell]")
        elif object.variable == "vg_j":
            cbar.set_label(f"J_{object.component} [nA/m**2]")
            ax.set_title(f"J_{object.component} [nA/m**2]")
        elif object.variable == "vg_derivatives/vg_dperbyvoldx":
            cbar.set_label("dB_y/dx [fT]")
            ax.set_title("dB_y/dx [fT] (f=femto [e-15])")
        elif object.variable == "vg_derivatives/vg_dperbzvoldx":
            cbar.set_label("dB_z/dx [fT]")
            ax.set_title("dB_z/dx [fT] (f=femto [e-15])")

        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_2D, frames = object.bulkfile_n + 1, interval = 20)

        writer = animation.PillowWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_2D(self, frame):
        self.p[0].remove()
        object = self.object
        fname = f"bulk.{str(frame).zfill(7)}.vlsv"
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)   

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[self.cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[self.cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, magnitude_mesh, self.level_boundaries)
        elif object.component == "deriv":
            value = np.array(vlsvobj.read_variable(object.variable)[self.cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, value_mesh, self.level_boundaries)
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[self.cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, value_mesh, self.level_boundaries)

        return self.p

    def animation_3D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cid_sort = self.cid_sort

        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')

        if object.component == "total":
            Min = 0
            Max = self.def_min_max()
        else:
            Min, Max = self.def_min_max()

        p = []
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            p.append(ax.plot_surface(self.x_mesh, self.y_mesh, magnitude_mesh, color=COLORS[0]))
        elif object.component == "deriv":
            value = np.array(vlsvobj.read_variable(object.variable)[cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            p.append(ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0]))
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            p.append(ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0]))
        
        self.p = p
        self.ax = ax

        if object.variable == "vg_b_vol":
            ax.set_zlabel(f"B_{object.component} [nT]")
            ax.set_title(f"B_{object.component} [nT]")
        elif object.variable == "proton/vg_v":
            ax.set_zlabel(f"v_{object.component} [km/s]")
            ax.set_title(f"v_{object.component} [km/s]")
        elif object.variable == "proton/vg_rho":
            ax.set_zlabel("rho [1e6/cell]")
            ax.set_title("rho [1e6/cell]")
        elif object.variable == "vg_j":
            ax.set_zlabel(f"J_{object.component} [nA/m**2]")
            ax.set_title(f"J_{object.component} [nA/m**2]")
        elif object.variable == "vg_derivatives/vg_dperbyvoldx":
            ax.set_zlabel("dB_y/dx [fT]")
            ax.set_title("dB_y/dx [fT] (f=femto [e-15])")
        elif object.variable == "vg_derivatives/vg_dperbzvoldx":
            ax.set_zlabel("dB_z/dx [fT]")
            ax.set_title("dB_z/dx [fT] (f=femto [e-15])")

        if object.variable == "vg_b_vol" and object.component == "x":
            ax.set_zlim(Min*0.9, Max*1.1)
        else:
            ax.set_zlim(Min, Max)
        
        ax.set_ylim(0, self.ymax)

        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, Max*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_3D, frames = object.bulkfile_n + 1, interval = 20)

        writer = animation.PillowWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_3D(self, frame):
        self.p[0].remove()
        object = self.object
        fname = f"bulk.{str(frame).zfill(7)}.vlsv"
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)   

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        if object.component == "total":
            y = np.array(vlsvobj.read_variable(object.variable, operator="y")[self.cid_sort]) / object.unit
            z = np.array(vlsvobj.read_variable(object.variable, operator="z")[self.cid_sort]) / object.unit
            magnitude = np.sqrt(y**2 + z**2)
            magnitude_mesh = magnitude.reshape(-1, self.x_length)
            self.p[0] = self.ax.plot_surface(self.x_mesh, self.y_mesh, magnitude_mesh, color = COLORS[0])
        elif object.component == "deriv":
            value = np.array(vlsvobj.read_variable(object.variable)[self.cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            self.p[0] = self.ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0])
        else:
            value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[self.cid_sort]) / object.unit
            value_mesh = value.reshape(-1, self.x_length)
            self.p[0] = self.ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0])

        return self.p
    
    def def_min_max(self):
        object = self.object
        values = []
        if object.component == "total":
            for i in range(10):
                fname = f"bulk.{str(i).zfill(7)}.vlsv"
                vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)
                y = vlsvobj.read_variable(object.variable,operator="y")/object.unit
                z =  vlsvobj.read_variable(object.variable,operator="z")/object.unit
                values.extend(np.sqrt(y**2 + z**2))
            return max(values)
        elif object.component == "deriv":
            for i in range(10):
                fname = f"bulk.{str(i).zfill(7)}.vlsv"
                vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)   
                values.extend(
                    vlsvobj.read_variable(object.variable)/object.unit)
        else:
            for i in range(10):
                fname = f"bulk.{str(i).zfill(7)}.vlsv"
                vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + fname)   
                values.extend(
                    vlsvobj.read_variable(object.variable,operator=object.component)/object.unit)
        return min(values), max(values)
    

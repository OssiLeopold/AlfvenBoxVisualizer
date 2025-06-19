import os
import analysator as pt
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from multiprocessing import shared_memory
from matplotlib import animation
import matplotlib as mpl
from matplotlib.animation import FFMpegWriter
plt.rcParams['animation.ffmpeg_path'] = "/home/rxelmer/Documents/turso/appl_local/ffmpeg/bin/ffmpeg"
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
        x_raw = np.array([vlsvobj.get_cell_coordinates(coord)[0] for coord in np.sort(self.cellids)])
        self.x_mesh = x.reshape(-1,self.x_length)
        self.y_mesh = y.reshape(-1,self.x_length)
        self.x_raw = x_raw
        
        # Bring to class scope
        self.vlsvobj = vlsvobj

        if self.object.animation_type == "2D":
            self.animation_2D()

        elif self.object.animation_type == "3D":
            self.animation_3D()

        elif self.object.animation_type == "fourier":
            self.animation_fourier()

    def animation_fourier(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")
        N = int(self.x_length)

        fig = plt.figure()
        ax = fig.add_subplot()
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
        value_x_direc_mesh = value.reshape(-1,100)
        value_y_direc_mesh = value_x_direc_mesh.T

        # Take Fourier transfrom from a slice in the middle in both directions
        value_ft = sp.fft.fft(value_x_direc_mesh[25])
        #value_ft_y = sp.fft.fft(value_y_direc_mesh[50])

        # Average of the two in both directions
        #value_ft = (value_ft_x + value_ft_y) / 2

        # Define spatial frequency. Delete first element due to zero value -> whould lead to infinite wavelength
        spatial_freq = sp.fft.fftfreq(N, np.diff(self.x_raw[0:N])[0])
        spatial_freq = np.delete(spatial_freq, 0)

        p = []
        p.append(ax.plot( 2*np.pi * spatial_freq[:N//2], np.abs(value_ft[:N//2])))
        spatial_freq_for_curve = np.delete(spatial_freq,0)
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2], 10**(-20) * (2*np.pi*spatial_freq_for_curve[:N//2])**(-2), label = "k**(-2)"))
        p.append(ax.plot(2*np.pi * spatial_freq_for_curve[:N//2], 10**(-18) * (2*np.pi*spatial_freq_for_curve[:N//2])**(-5/3), label = "k**(-5/3)"))

        self.p = p
        self.ax = ax

        ax.set_title(f"Fourier transform of {object.variable_name}")
        ax.set_xlabel("k")
        ax.set_ylabel("Not quite sure")
        ax.set_ylim(1e-11,1e-7)
        for i in range(1,10):
            ax.axvline(x = 2 * np.pi / (1.5*10**7 / i), lw = 0.5)
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(axis="y")
        ax.legend()

        self.timelabel = ax.text(max(spatial_freq), max(np.abs(value_ft))*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_fourier, frames = object.bulkfile_n + 1, interval = 20)
        
        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_fourier(self, frame):
        N = int(self.x_length)
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")

        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()])
        value_x_direc_mesh = value.reshape(-1,100)
        #value_y_direc_mesh = value_x_direc_mesh.T

        value_ft = sp.fft.fft(value_x_direc_mesh[25])
        #value_ft_y = sp.fft.fft(value_y_direc_mesh[50])
    
        #value_ft = value_ft_x + value_ft_y
        value_ft = np.delete(value_ft, 0)

        spatial_freq = sp.fft.fftfreq(N, np.diff(self.x_raw[0:N])[0])
        spatial_freq = np.delete(spatial_freq, 0)

        self.p[0][0].set_data(2*np.pi*spatial_freq[:N//2-1], np.abs(value_ft[:N//2-1]))

        return self.p

    def animation_2D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")

        fig = plt.figure()
        ax = fig.add_subplot()

        Min, Max = self.def_min_max()

        levels = 300
        level_boundaries = np.linspace(Min, Max, levels + 1)
        self.level_boundaries = level_boundaries

        p = []
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        p.append(ax.contourf(self.x_mesh, self.y_mesh, value_mesh, level_boundaries))
        
        self.p = p
        self.ax = ax

        cbar = plt.colorbar(p[0])
        cbar.set_label(f"{object.variable_name} [{object.unit_name}]")
        ax.set_title(f"{object.variable_name} [{object.unit_name}]")

        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_2D, frames = object.bulkfile_n + 1, interval = 20)

        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_2D(self, frame):
        self.p[0].remove()
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
        cellids = vlsvobj.read_variable("CellID")   

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        self.p[0] = self.ax.contourf(self.x_mesh, self.y_mesh, value_mesh, self.level_boundaries)

        return self.p

    def animation_3D(self):
        vlsvobj = self.vlsvobj
        object = self.object
        cellids = vlsvobj.read_variable("CellID")

        fig = plt.figure()
        ax = fig.add_subplot(projection = '3d')

        Min, Max = self.def_min_max()

        p = []
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        p.append(ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0]))
    
        self.p = p
        self.ax = ax

        ax.set_zlabel(f"{object.variable_name} [{object.unit_name}]")
        ax.set_title(f"{object.variable_name} [{object.unit_name}]")

        if object.variable == "vg_b_vol" and object.component == "x":
            ax.set_zlim(Min*0.9, Max*1.1)
        else:
            ax.set_zlim(Min, Max)
        
        ax.set_ylim(0, self.ymax)

        ax.set_xlabel("x [RE]")
        ax.set_ylabel("y [RE]")
        self.timelabel = ax.text(self.xmax, self.ymax*1.01, Max*1.01, "")

        anim = animation.FuncAnimation(fig, self.update_3D, frames = object.bulkfile_n + 1, interval = 20)

        writer = FFMpegWriter(fps=5)
        anim.save(object.name, writer = writer)
        plt.close()

    def update_3D(self, frame):
        self.p[0].remove()
        object = self.object
        vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")  
        cellids = vlsvobj.read_variable("CellID")

        time = vlsvobj.read_parameter("time")
        self.timelabel.set_text(f"{time:.1f}s")
        
        value = np.array(vlsvobj.read_variable(object.variable, operator=object.component)[cellids.argsort()]) / object.unit
        value_mesh = value.reshape(-1, self.x_length)
        self.p[0] = self.ax.plot_surface(self.x_mesh, self.y_mesh, value_mesh, color = COLORS[0])

        return self.p
    
    def def_min_max(self):
        object = self.object
        values = []
        for i in range(object.bulkfile_n):
            vlsvobj = pt.vlsvfile.VlsvReader(object.bulkpath + f"bulk.{str(i).zfill(7)}.vlsv")   
            values.extend(
                vlsvobj.read_variable(object.variable,operator=object.component)/object.unit)
        """ for i in range(object.bulkfile_n - 5, object.bulkfile_n):
            vlsvobj = self.bulkfiles[i]   
            values.extend(
                vlsvobj.read_variable(object.variable,operator=object.component)/object.unit) """
        return min(values), max(values)
    

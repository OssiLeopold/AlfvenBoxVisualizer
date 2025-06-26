import analysator as pt
import matplotlib.pyplot as plt
import os
from matplotlib import animation
from matplotlib.animation import FFMpegWriter
import numpy as np
import statistics
import seaborn as sns
plt.rcParams['animation.ffmpeg_path'] = "/home/rxelmer/Documents/turso/appl_local/ffmpeg/bin/ffmpeg"

os.environ['PATH']='/home/rxelmer/Documents/turso/appl_local/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] 
os.environ['PTNOLATEX']='1'
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim18/"

fig, axes = plt.subplots(3,3,figsize=(12,12))
axes = axes.flatten()

titles = ["delta_l2", "delta_l4", "delta_l6", "delta_l8", "delta_l10", "delta_l12", "delta_l20","delta_l24","delta_l38"]

def update(frame):
    # Clear axes for new frame
    for ax in axes:
        ax.clear()

    # Fetch data from bulkfile
    vlsvobj = pt.vlsvfile.VlsvReader(bulkpath + f"bulk.{str(frame).zfill(7)}.vlsv")
    cellids = vlsvobj.read_variable("CellID")
    value = np.array(vlsvobj.read_variable("vg_b_vol", operator = "y"))[cellids.argsort()]

    # Create two 2D_arrays. One in the x direction and one in the y direction
    value_mesh_x = value.reshape(-1,100)
    value_mesh_y = value_mesh_x.T
    
    # Calculate statistical parameters from data in each frame
    mean = statistics.mean(value)
    SD = statistics.stdev(value)
    
    # Create empty arrays for 
    delta_l2 = []
    delta_l4 = []
    delta_l6 = []
    delta_l8 = []
    delta_l10 = []
    delta_l12 = []
    delta_l20 = []
    delta_l24 = []
    delta_l38 = []

    L = 100

    # Loop through all slices
    #for i in range(len(value_mesh_x)):
    value_slice_x = value_mesh_x[50]
    value_slice_y = value_mesh_y[50]

    for j in range(0,L,2):
        if j + 2 >= L:
            delta_l2.append((value_slice_x[j+2-L]-value_slice_x[j]-mean)/SD)
            delta_l2.append((value_slice_y[j+2-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l2.append((value_slice_x[j+2]-value_slice_x[j]-mean)/SD)
            delta_l2.append((value_slice_y[j+2]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,4):
        if j + 4 >= L:
            delta_l4.append((value_slice_x[j+4-L]-value_slice_x[j]-mean)/SD)
            delta_l4.append((value_slice_y[j+4-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l4.append((value_slice_x[j+4]-value_slice_x[j]-mean)/SD)
            delta_l4.append((value_slice_y[j+4]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,6):
        if j + 6 >= L:
            delta_l6.append((value_slice_x[j+6-L]-value_slice_x[j]-mean)/SD)
            delta_l6.append((value_slice_y[j+6-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l6.append((value_slice_x[j+6]-value_slice_x[j]-mean)/SD)
            delta_l6.append((value_slice_y[j+6]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,8):
        if j + 8 >= L:
            delta_l8.append((value_slice_x[j+8-L]-value_slice_x[j]-mean)/SD)
            delta_l8.append((value_slice_y[j+8-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l8.append((value_slice_x[j+8]-value_slice_x[j]-mean)/SD)
            delta_l8.append((value_slice_y[j+8]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,10):
        if j + 10 >= L:
            delta_l10.append((value_slice_x[j+10-L]-value_slice_x[j]-mean)/SD)
            delta_l10.append((value_slice_y[j+10-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l10.append((value_slice_x[j+10]-value_slice_x[j]-mean)/SD)
            delta_l10.append((value_slice_y[j+10]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,12):
        if j + 12 >= L:
            delta_l12.append((value_slice_x[j+12-L]-value_slice_x[j]-mean)/SD)
            delta_l12.append((value_slice_y[j+12-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l12.append((value_slice_x[j+12]-value_slice_x[j]-mean)/SD)
            delta_l12.append((value_slice_y[j+12]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,20):
        if j + 20 >= L:
            delta_l20.append((value_slice_x[j+20-L]-value_slice_x[j]-mean)/SD)
            delta_l20.append((value_slice_y[j+20-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l20.append((value_slice_x[j+20]-value_slice_x[j]-mean)/SD)
            delta_l20.append((value_slice_y[j+20]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,24):
        if j + 24 >= L:
            delta_l24.append((value_slice_x[j+24-L]-value_slice_x[j]-mean)/SD)
            delta_l24.append((value_slice_y[j+24-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l24.append((value_slice_x[j+24]-value_slice_x[j]-mean)/SD)
            delta_l24.append((value_slice_y[j+24]-value_slice_y[j]-mean)/SD)

    for j in range(0,L,38):
        if j + 38 >= L:
            delta_l38.append((value_slice_x[j+38-L]-value_slice_x[j]-mean)/SD)
            delta_l38.append((value_slice_y[j+38-L]-value_slice_y[j]-mean)/SD)
        else:
            delta_l38.append((value_slice_x[j+38]-value_slice_x[j]-mean)/SD)
            delta_l38.append((value_slice_y[j+38]-value_slice_y[j]-mean)/SD)


    deltas = [delta_l2,delta_l4,delta_l6,delta_l8,delta_l10,delta_l12,delta_l20,delta_l24,delta_l38]

    gaussian = np.random.normal(mean, SD, 10000)/SD

    for i, ax in enumerate(axes):
        sns.kdeplot(gaussian, ls = ":",ax=ax)
        ax.hist(deltas[i], bins=10, density=True)
        ax.set_title(titles[i])
        ax.set_xlim(-6,6)
        ax.set_yscale("log")
        ax.set_ylim(1e-3,1)

anim = animation.FuncAnimation(fig, update, frames = 100, interval = 20)

writer = FFMpegWriter(fps=5)
anim.save("struct_By_sim18_hist_one_xy_10bins_density_log_gauss_jump.mp4", writer=writer)
plt.close()
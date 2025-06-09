import os
os.environ['PATH']='/home/rxelmer/Documents/turso/appl/tex-basic/texlive/2023/bin/x86_64-linux:'+ os.environ['PATH'] #enabling use of latex
os.environ['PTNOLATEX']='1' #enabling use of latex

# Import packages
import multiprocessing as mp        # For multiprocessing

# Import user defined classes
from anim_specs import AnimSpecs
import animator


    
# Set path where to find simulation bulk files
bulkpath = "/home/rxelmer/Documents/turso/bulks/sim15/"



# Enter number of bulkfiles, for example if your last bulkfile is named bulk.0000100.vlsv -> then enter 100, or the specific amount of frames you want to animate
bulkfile_n = 10

#animations = [("3D", "B_y","anim1.gif"),("2D", "v_tot","anim2.gif"), ("3D", "v_z","anim3.gif")]
animations = [("2D", "B_tot","anim1.gif"),("2D", "v_tot","anim2.gif")]

for i in range(len(animations)):
    animations[i] = AnimSpecs(animations[i][0], animations[i][1], animations[i][2], bulkpath, bulkfile_n)

with mp.Pool(len(animations)) as process:
    process.map(animator.animatorFunc, animations)


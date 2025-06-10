import sys

# Dictionary for translating instructions for VlsvReader
translate = {"B_x":("vg_b_vol", "x", 1e-9),
                "B_y":("vg_b_vol", "y", 1e-9),
                "B_z":("vg_b_vol", "z", 1e-9),
                "dB_y/dx":("vg_derivatives/vg_dperbyvoldx", "deriv", 1e-15),
                "dB_z/dx":("vg_derivatives/vg_dperbzvoldx", "deriv", 1e-15),
                "B_tot":("vg_b_vol", "total", 1e-9),
                "J_y":("vg_j", "y", 1e-9),
                "J_z":("vg_j", "z", 1e-9),
                "v_x":("proton/vg_v", "x", 1e3),
                "v_y":("proton/vg_v", "y", 1e3),
                "v_z":("proton/vg_v", "z", 1e3),
                "v_tot":("proton/vg_v", "total", 1e3),
                "rho":("proton/vg_rho", "pass", 1e6)}

# Defining AnimationSpecs object and checking instructions
class AnimationSpecs():
    def __init__(self, animation_type, variable, name, bulkpath, bulkfile_n):
        if animation_type not in ["3D", "2D"]:
            print("animation_type defined incorrectly")
            sys.exit(1)

        if variable not in ["B_y", "B_z", "B_x", "dB_y/dx", "dB_z/dx", "B_tot", "J_y", "J_z", "v_y", "v_z", "v_x", "v_tot", "rho"]:
            print("variable defined incorrectly")
            sys.exit(1)

        if name[-3:] != "gif":
            print("filetype defined incorrectly")
            sys.exit(1)

        self.animation_type = animation_type
        self.variable = translate[variable][0]
        self.component = translate[variable][1]
        self.unit = translate[variable][2]
        self.name = name
        self.bulkpath = bulkpath
        self.bulkfile_n = bulkfile_n
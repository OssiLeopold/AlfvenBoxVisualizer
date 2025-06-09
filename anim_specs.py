import sys

translations = {"B_y":("vg_b_vol", "y", 1e-9),
                "B_z":("vg_b_vol", "z", 1e-9),
                "B_tot":("vg_b_vol", "total", 1e-9),
                "v_y":("proton/vg_v", "y", 1e3),
                "v_z":("proton/vg_v", "z", 1e3),
                "v_tot":("proton/vg_v", "total", 1e3),
                "rho":"proton/vg_rho"}

class AnimSpecs():
    def __init__(self, animation_type, variable, name, bulkpath, bulkfile_n):
        if animation_type not in ["3D", "2D"]:
            print("animation_type defined incorrectly")
            sys.exit(1)
        if variable not in ["B_y", "B_z", "B_tot", "v_y", "v_z", "v_tot", "rho"]:
            print("variable defined incorrectly")
            sys.exit(1)
        if name[-3:] != "gif":
            print("filetype defined incorrectly")
            sys.exit(1)
        self.animation_type = animation_type
        self.variable = translations[variable][0]
        self.component = translations[variable][1]
        self.unit = translations[variable][2]
        self.name = name
        self.bulkpath = bulkpath
        self.bulkfile_n = bulkfile_n
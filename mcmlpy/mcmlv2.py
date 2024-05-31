# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string
# pylint: disable=too-many-statements
# pylint: disable=broad-exception-caught

import numpy as np
import matplotlib.pyplot as plt

from mcmlpy import MCML, skip_to_line_after, read_N_floats, read_next_line

__all__ = ['MCMLV2']

class MCMLV2(MCML):
    def __init__(self):
        super().__init__()
        self.magic = 'mcmloA2.0'
        self.media = {}
        self.num_layers = 0
        self.layer_name = np.array([], dtype=float)
        self.source_type = 'pencil'
        self.source_depth = 0
        self.dt = np.array([], dtype=float)
        self.ndt = 1
        self.Tdr = np.array([], dtype=float)
        self.Tda = np.array([], dtype=float)
        self.Tdra = np.array([], dtype=float)

    def __str__(self):
        s = super().__str__()
        s += 't_bins = %4d, ' % self.ndt
        s += 'dt = %.3f ps\n'  % self.dt
        s += '\n'
        for i in range(self.num_layers):
            s += 'layer %d: ' % (i + 1)
            s += '%s\n' % self.layer_name[i]
            s += '    n=%5.3f ' % self.n[i]
            s += 'µa=%.2fmm⁻¹ ' % self.mu_a[i]
            s += 'µs=%.2fmm⁻¹ ' % self.mu_s[i]
            s += 'g=%.2f ' % self.g[i]
            if np.isinf(self.d[i]):
                s += 'd=infinite\n' % self.d[i]
            else:
                s += 'd=%.2fmm\n' % self.d[i]
        return s

    def read_layers(self, file):
        """Read the layer information from the V2 .mco file."""
        #initialize layers
        self.num_layers = 0
        self.n = np.array([], dtype=float)
        self.mu_a = np.array([], dtype=float)
        self.mu_s = np.array([], dtype=float)
        self.g = np.array([], dtype=float)
        self.d = np.array([], dtype=float)
        self.layer_name = []

        # read media
        media = {}
        s = read_next_line(file)
        while s != 'end':
            x = s.split()
            media[x[0]] = np.array(x[1:], dtype=float)
            s = read_next_line(file)

        # skip filename
        s = read_next_line(file)

        # read layers
        s = read_next_line(file)
        while s != 'end':
            x = s.split()
            self.layer_name.append(x[0])
            if len(x)==1:
                self.d = np.append(self.d, np.inf)
            else:
                self.d = np.append(self.d, float(x[1])*10)  # mm
            prop = media[x[0]]
            self.n    = np.append(self.n,    float(prop[0]))
            self.mu_a = np.append(self.mu_a, float(prop[1])/10) # per mm
            self.mu_s = np.append(self.mu_s, float(prop[2])/10) # per mm
            self.g    = np.append(self.g,    float(prop[3]))
            self.num_layers += 1
            s = read_next_line(file)

    def init_from_v2_file(self, file):
        skip_to_line_after(file, 'mcmli2.0')

        self.read_layers(file)

        #read source info
        self.source_type = read_next_line(file)
        self.source_depth = float(read_next_line(file))

        s = read_next_line(file)
        self.dz, self.dr, self.dt = s.split()
        self.dr = float(self.dr) * 10  # convert from cm to mm
        self.dz = float(self.dz) * 10  # convert from cm to mm
        self.dt = float(self.dt)

        s = read_next_line(file)
        ndz, ndr, ndt, nda = s.split()
        self.ndz = int(ndz)
        self.ndr = int(ndr)
        self.ndt = int(ndt)
        self.nda = int(nda)

        # create radii and depth arrays
        self.r = np.linspace(0, self.ndr - 2, int(self.ndr - 1)) * self.dr
        self.z = np.linspace(0, self.ndz - 1, int(self.ndz)) * self.dz

# left to do
#   Rd_ra   Rd_t    Rd_rt   Rd_at   Rd_rat
#   Td_ra   Td_t    Td_rt   Td_at   Td_rat
#   A_zt    A_rzt

        if skip_to_line_after(file, "RAT"):
            self.Rsp        = float(read_next_line(file).split()[0])
            self.Ru         = float(read_next_line(file).split()[0])
            self.Rd         = float(read_next_line(file).split()[0])
            self.Rt         = self.Ru + self.Rd
            self.absorbed   = float(read_next_line(file).split()[0])
            self.Tu         = float(read_next_line(file).split()[0])
            self.Td         = float(read_next_line(file).split()[0])
            self.Tt         = self.Tu + self.Td

        if skip_to_line_after(file, "A_z", occurrence=2):
            self.Az = read_N_floats(file, self.ndz)
            self.Az = self.Az[:-1]
            self.Az /= 10 # convert from cm⁻¹ to mm⁻¹

        if skip_to_line_after(file, "Rd_r", occurrence=2):
            self.Rdr = read_N_floats(file, self.ndr)
            self.Rdr = self.Rdr[:-1]
            self.Rdr /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Rd_a", occurrence=2):
            self.Rda = np.genfromtxt(file, max_rows=self.nda, dtype=float).flatten()

        if skip_to_line_after(file, "Td_r", occurrence=2):
            self.Tdr = read_N_floats(file, self.ndr)
            self.Tdr = self.Tdr[:-1]
            self.Tdr /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Td_a", occurrence=2):
            self.Tda = np.genfromtxt(file, max_rows=self.nda, dtype=float).flatten()

        if skip_to_line_after(file, "A_rz", occurrence=2):
            Arz = read_N_floats(file, self.ndz * self.ndr)
            self.Arz = Arz.reshape(self.ndr, self.ndz).T
            self.Arz /= 1000  # convert from cm⁻² to mm⁻²
            np.place(self.Arz, self.Arz < 1e-8, 1e-8)

        if skip_to_line_after(file, "Rd_ra", occurrence=2):
            Rdra = read_N_floats(file, self.nda * self.ndr)
            self.Rdra = Rdra.reshape(self.ndr, self.nda).T
            self.Rdra /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Td_ra", occurrence=2):
            self.Tdra = read_N_floats(file, self.nda * self.ndr)
            self.Tdra /= 100  # convert from cm⁻² to mm⁻²

    def init_from_file(self, fname):
        try:
            with open(fname, 'r', encoding='utf-8') as file:
                if self.verify_magic(file):
                    self.init_from_v2_file(file)
                else:
                    print('unknown file format')
        except FileNotFoundError:
            print(f"Failed to open the file {fname}: File not found.")
        except PermissionError:
            print(f"Failed to open the file {fname}: Permission denied.")
        except UnicodeDecodeError:
            print(f"Failed to read the file {fname}: Unicode decoding error with UTF-8.")
        except Exception as e:  # Still catching Exception but now it's more justified
            print(f"An unexpected error occurred while initializing from file {fname}: {e}")

    def add_plot_text(self, top=0.98):
        dv = 0.06
        v = top
        for i in range(self.num_layers):
            s = '%s: ' % self.layer_name[i]
            s += r'$\mu_a$=%.2f ' % self.mu_a[i]
            s += r'$\mu_s$=%.2f ' % self.mu_s[i]
            s += r'g=%.2f ' % self.g[i]
            s += r'd=%.2f ' % self.d[i]
            plt.text(0.65, v, s, ha='left', va='top', transform=plt.gca().transAxes, fontsize=8)
            v = v - dv

# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string
# pylint: disable=too-many-statements
# pylint: disable=broad-exception-caught

import numpy as np
import matplotlib.pyplot as plt

from mcmlpy import MCML, skip_to_line_after, read_N_floats

__all__ = ['MCMLV1']

class MCMLV1(MCML):
    def __init__(self):
        super().__init__()
        self.magic = 'A1'

    def __str__(self):
        s = super().__str__()
        s += '\n'
        s += 'above:\n'
        s += '    n=%5.3f\n' % self.n_above
        for i in range(self.num_layers):
            s += 'layer %d:\n' % (i + 1)
            s += '    n=%5.3f ' % self.n[i]
            s += 'mu_a=%.2f mm⁻¹ ' % self.mu_a[i]
            s += 'mu_s=%.2f mm⁻¹ ' % self.mu_s[i]
            s += 'g=%.2f ' % self.g[i]
            s += 'd=%.2f mm\n' % self.d[i]
        s += 'below:\n'
        s += '    n=%5.3f\n' % self.n_below
        return s

    def read_layers(self, file):
        self.num_layers = np.genfromtxt(file, max_rows=1, dtype=int)

        self.n_above = np.genfromtxt(file, skip_header=1, max_rows=1, dtype=float)

        for _ in range(self.num_layers):
            x = np.genfromtxt(file, max_rows=1, dtype=float)
            self.n = np.append(self.n, x[0])
            self.mu_a = np.append(self.mu_a, x[1]/10) # cm⁻¹ to mm⁻¹
            self.mu_s = np.append(self.mu_s, x[2]/10) # cm⁻¹ to mm⁻¹
            self.g = np.append(self.g, x[3])
            self.d = np.append(self.d, x[4]*10) # cm to mm

        self.n_below = np.genfromtxt(file, max_rows=1, dtype=float)

    def init_from_v1_file(self, file):
        file.seek(0)
        photons = np.genfromtxt(file, skip_header=13, max_rows=1)
        self.photons = int(photons)

        self.dz, self.dr = np.genfromtxt(file, max_rows=1)
        self.dr *= 10  # convert from cm to mm
        self.dz *= 10  # convert from cm to mm

        ndz, ndr, nda = np.genfromtxt(file, max_rows=1)
        self.ndz = int(ndz)
        self.ndr = int(ndr)
        self.nda = int(nda)

        # create radii and depth arrays
        self.r = np.linspace(0, self.ndr - 2, int(self.ndr - 1)) * self.dr
        self.z = np.linspace(0, self.ndz - 1, int(self.ndz)) * self.dz
        
        self.read_layers(file)

        if skip_to_line_after(file, "RAT"):
            self.Rsp = np.genfromtxt(file, max_rows=1, dtype=float)
            self.Ru  = self.Rsp
            self.Rd = np.genfromtxt(file, max_rows=1, dtype=float)
            self.Rt = self.Rd + self.Ru
            self.absorbed = np.genfromtxt(file, max_rows=1, dtype=float)
            self.Td = np.genfromtxt(file, max_rows=1, dtype=float)
            self.Tt = self.Td
            self.Tu = 0

        if skip_to_line_after(file, "A_z"):
            self.Az = np.genfromtxt(file, max_rows=self.ndz).flatten()
            self.Az = self.Az[:-1]
            self.Az /= 10 # convert from cm⁻¹ to mm⁻¹

        if skip_to_line_after(file, "Rd_r"):
            self.Rdr = np.genfromtxt(file, max_rows=self.ndr).flatten()
            self.Rdr = self.Rdr[:-1]
            self.Rdr /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Rd_a"):
            self.Rda = np.genfromtxt(file, max_rows=self.nda).flatten()

        if skip_to_line_after(file, "Tt_r"):
            self.Ttr = np.genfromtxt(file, max_rows=self.ndr).flatten()
            self.Ttr = self.Ttr[:-1]
            self.Ttr /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Tt_a"):
            self.Tta = np.genfromtxt(file, max_rows=self.nda).flatten()

        if skip_to_line_after(file, "A_rz"):
            Arz = read_N_floats(file, self.ndz * self.ndr)
            self.Arz = Arz.reshape(self.ndr, self.ndz).T
            self.Arz /= 1000  # convert from cm⁻² to mm⁻²
            np.place(self.Arz, self.Arz < 1e-8, 1e-8)

        if skip_to_line_after(file, "Rd_ra"):
            Rdra = read_N_floats(file, self.nda * self.ndr)
            self.Rdra = Rdra.reshape(self.ndr, self.nda).T
            self.Rdra /= 100  # convert from cm⁻² to mm⁻²

        if skip_to_line_after(file, "Tt_ra"):
            self.Ttra = read_N_floats(file, self.nda * self.ndr)
            self.Ttra /= 100  # convert from cm⁻² to mm⁻²

    def init_from_file(self, fname):
        try:
            with open(fname, 'r', encoding='utf-8') as file:
                if self.verify_magic(file):
                    self.init_from_v1_file(file)
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
            s = '%d: ' % (i + 1)
            s += r'$\mu_a$=%.2f ' % self.mu_a[i]
            s += r'$\mu_s$=%.2f ' % self.mu_s[i]
            s += r'g=%.2f ' % self.g[i]
            s += r'd=%.2f ' % self.d[i]
            plt.text(0.65, v, s, ha='left', va='top', transform=plt.gca().transAxes, fontsize=8)
            v = v - dv

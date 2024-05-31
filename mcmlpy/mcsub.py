# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string
# pylint: disable=too-many-statements
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals

import numpy as np
import matplotlib.pyplot as plt

from mcmlpy import MCML

__all__ = ['MCSub']

class MCSub(MCML):

    def __init__(self, mu_a=0, mu_s=0, g=0, n_tissue=1, n_above=1, mcflag=0,
                 beam_radius=0, beam_waist=0, x_source=0, y_source=0, z_source=0,
                 rbins=1, zbins=1, dr=0.1, dz=0.1, photons=100000,
                 r_specular=0, absorbed=0, escaping=0, refl=None, fluence=None, z=None, r=None):
        super().__init__()
        self.n_above = n_above
        self.num_layers = 1
        self.mu_a = np.zeros(1)
        self.mu_s = np.zeros(1)
        self.g = np.zeros(1)
        self.n = np.zeros(1)
        self.mu_a[0] = mu_a
        self.mu_s[0] = mu_s
        self.g[0] = g
        self.n[0] = n_tissue
        self.mcflag = int(mcflag)
        self.beam_radius = beam_radius
        self.beam_waist = beam_waist
        self.x_source = x_source
        self.y_source = y_source
        self.z_source = z_source
        self.ndr = int(rbins)
        self.ndz = int(zbins)
        self.dr = dr
        self.dz = dz
        self.photons = int(photons)
        self.Ru = r_specular
        self.absorbed = absorbed
        self.Rd = escaping
        self.Rt = self.Ru + self.Rd
        self.Rdr = refl
        self.Arz = fluence
        self.z = z
        self.r = r

    def init_from_mcsub_file(self, file):
        params = np.genfromtxt(file, comments='\t', max_rows=19)
        
        self.mu_a[0] = params[0]
        self.mu_s[0] = params[1]
        self.g[0] = params[2]
        self.n[0] = params[3]
        self.n_above = params[4]
        self.mcflag = int(params[5])
        self.beam_radius = params[6]
        self.beam_waist = params[7]
        self.x_source = params[8]
        self.y_source = params[9]
        self.z_source = params[10]
        self.ndr = int(params[11])
        self.ndz = int(params[12])
        self.dr = params[13]
        self.dz = params[14]
        self.photons = int(params[15])
        self.Ru = params[16]
        self.absorbed = params[17]
        self.Rd = params[18]
        self.Rt = self.Rd + self.Ru

        # read reflectance as a function of radius, discard first and last entries
        self.r = np.genfromtxt(file, delimiter='\t', max_rows=1)[:-2]
        self.r -= self.r[0]  # set to the left edge of each pixel
        self.Rdr = np.genfromtxt(file, delimiter='\t', max_rows=1)[1:-1]

        self.r = np.linspace(0, self.ndr - 2, int(self.ndr - 1)) * self.dr

        # read fluence and extract z values
        fluence = np.genfromtxt(file)
        np.place(fluence, fluence == 0, 1e-10)
        self.z = fluence[:-1, 0]
        self.z -= self.dz / 2  # set to top of bin
        self.Arz = fluence[:-1, 1:-1]

        # convert to mm
        self.mu_a[0] /= 10         # mm⁻¹
        self.mu_s[0] /= 10         # mm⁻¹
        self.beam_radius *= 10  # mm
        self.beam_waist *= 10   # mm
        self.x_source *= 10     # mm
        self.y_source *= 10     # mm
        self.z_source *= 10     # mm
        self.dz *= 10           # mm
        self.dr *= 10           # mm
        self.z *= 10            # mm
        self.r *= 10            # mm
        self.Rdr /= 100         # W/mm²
        self.Arz /= 100         # W/mm²

    def init_from_file(self, fname):
        try:
            with open(fname, 'r', encoding='utf8') as file:
                self.init_from_mcsub_file(file)

        except Exception as e:
            print(f"Failed to initialize from file {fname} with error: {e}")

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
            s += 'd=infinite\n'
        s += '\n'

        if self.mcflag == 0:
            s += 'flat top beam radius = %g mm\n' % self.beam_radius
        elif self.mcflag == 1:
            s += 'Gaussian 1/e² surface radius = %g mm\n' % self.beam_radius
            s += 'Gaussian 1/e²   focus radius = %g mm\n' % self.beam_waist
            s += '                focus  depth = %g mm\n' % self.z_source
        else:
            s += 'isotropic source at = (%g, %g, %g) mm\n' % \
                 (self.x_source, self.y_source, self.z_source)
        return s

    def add_plot_text(self, top=0.95):
        dv = 0.06
        v = top
        s = r'$\mu_s$ = %.2f mm⁻¹' % self.mu_s[0]
        plt.text(0.95, v, s, ha='right', va='top', transform=plt.gca().transAxes)
        s = r'$\mu_a$ = %.2f mm⁻¹' % self.mu_a[0]
        plt.text(0.95, v - dv, s, ha='right', va='top', transform=plt.gca().transAxes)
        s = r'g = %.3f' % self.g[0]
        plt.text(0.95, v - 2 * dv, s, ha='right', va='top', transform=plt.gca().transAxes)
        s = r'n$_{tissue}$ = %.3f' % self.n[0]
        plt.text(0.95, v - 3 * dv, s, ha='right', va='top', transform=plt.gca().transAxes)
        s = r'n$_{env}$ = %.3f' % self.n_above
        plt.text(0.95, v - 4 * dv, s, ha='right', va='top', transform=plt.gca().transAxes)

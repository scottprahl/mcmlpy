# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string

import re
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter
from matplotlib import cm, colors

__all__ = ['read_N_floats',
           'skip_to_line_after',
           'read_next_line',
           'MCML'
          ]

def read_float(file):
    buffer = ''
    while True:
        chunk = file.read(1)  # Read one character at a time
        if not chunk:  # End of file
            break
        if chunk.isspace() and buffer:  # End of a number
            break
        if chunk.isdigit() or chunk in '.-+eE':  # Part of a float
            buffer += chunk
        elif buffer:  # Already started reading a number, then encountered a non-number
            break
    try:
        return float(buffer)
    except ValueError:
        return None


def read_N_floats(file, N):
    arr = np.zeros(N)
    for i in range(N):
        arr[i] = read_float(file)
    return arr


def read_next_line(fp):
    length = 0
    while length==0:
        s = fp.readline()
        s = s.split('#', 1)[0]      # Discard comments
        s = re.sub(r'\s+', ' ', s)  # Compress whitespace to a single space
        s = s.strip()               # Discard leading and trailing whitespace
        length = len(s)
    return s


def skip_to_line_after(fp, target, occurrence=1):
    """
    Sets the file pointer to the line immediately after the one containing the target.

    This function reads through the file line by line, searching each line for a given target
    string. Once the target string has been found a specified number of times (occurrence),
    it advances the file pointer to the next line and returns True. If the end of the file
    is reached without finding the target string the required number of times, it returns False.

    Anything after '#' is considered a comment and ignored.

    Args:
        fp (file object): The file pointer of an open file.
        target (str): The string to search for within the file.
        occurrence (int, optional): The number of target to find before stopping.

    Returns:
        True if the target string is found the specified number of times. False otherwise
    """
    fp.seek(0)
    count = 0

    for line in fp:
        line = line.split('#', 1)[0].strip()  # Discard comments and strip whitespace
        if target in line:
            count += 1
            if count == occurrence:
                break

    return count == occurrence

class MCML:
    """
    A class to import output from the MCML program.

    This is a super class for MCMLV1 and MCMLV2 .mco files.

    Attributes:
        magic (str): Identifier for the file format .
        photons (int): Number of photon packets used in the simulation.
        dz (float): Thickness of the grid layers in the z-direction (axial).
        dr (float): Radial resolution of the grid.
        ndz (int): Number of divisions in the z-direction.
        ndr (int): Number of divisions in the radial direction.
        nda (int): Number of angular divisions; not explicitly used here.
        num_layers (int): Number of layers in the tissue.
        n_above (float): Refractive index environment above the tissue.
        n (numpy.ndarray): Refractive indices of the tissue layers.
        mu_a (numpy.ndarray): Absorption coefficients of the tissue layers (in mm⁻¹).
        mu_s (numpy.ndarray): Scattering coefficients of the tissue layers (in mm⁻¹).
        g (numpy.ndarray): Anisotropy factors of the tissue layers.
        d (numpy.ndarray): Thicknesses of each tissue layer (in mm).
        n_below (float): Refractive index below the tissue.
        Rsp (float): Specular reflectance at the interface (dimensionless).
        Rd (float): Diffuse reflectance.
        Ru (float): Unscattered reflectance.
        Td (float): Diffuse transmittance.
        Tu (float): Unscattered transmittance.
        absorbed (float): Total absorbed energy (Watts).
        Az (numpy.ndarray): Axial absorbance as a function of depth.
        Rdr (numpy.ndarray): Radial distribution of diffuse reflectance.
        Rda (numpy.ndarray): Angular distribution of diffuse reflectance.
        Ttr (numpy.ndarray): Radial distribution of transmitted energy.
        Tta (numpy.ndarray): Angular distribution of transmitted energy.
        Arz (numpy.ndarray): Absorption distribution as a function of radial and axial positions.
        Rdra (numpy.ndarray): Diffuse reflectance as a function of radial and angular positions.
        Ttra (numpy.ndarray): Transmitted reflectance as a function of radial and angular positions.
        r (numpy.ndarray): Radial positions corresponding to the values in the radial profiles.
        z (numpy.ndarray): Axial positions corresponding to the values in the axial profiles.
    """
    def __init__(self):
        self.magic = ''
        self.photons = 0
        self.ndz = 0
        self.ndr = 0
        self.nda = 0
        self.num_layers = 0

        self.dz = 0
        self.dr = 0

        self.r = np.array([])
        self.z = np.array([])

        self.n_above = 1
        self.n = np.array([])
        self.mu_a = np.array([])
        self.mu_s = np.array([])
        self.g = np.array([])
        self.d = np.array([])
        self.n_below = 1

        self.Rsp = 0
        self.Ru = 0
        self.Rd = 0
        self.Rt = 0
        self.Tu = 0
        self.Td = 0
        self.Tt = 0
        self.absorbed = 0
        self.Az = np.array([])
        self.Rdr = np.array([])
        self.Rda = np.array([])
        self.Ttr = np.array([])
        self.Tta = np.array([])
        self.Arz = np.array([])
        self.Rdra = np.array([])
        self.Ttra = np.array([])

    def verify_magic(self, fp):
        """
        Verify that the file's initial bytes match the 'magic' attribute of the class.
        """
        fp.seek(0)
        chunk = fp.read(len(self.magic))
        fp.seek(0)
        return chunk==self.magic

    def __str__(self):
        """
        A string describing the contents of the class.
        """
        s = ''
        s += 'photons       = %d\n'    % self.photons
        s += '\n'
        s += 'R_unscattered = %8.5f\n' % self.Ru
        s += 'R_scattered   = %8.5f\n' % self.Rd
        s += 'R_total       = %8.5f\n' % (self.Rd + self.Ru)
        s += 'T_unscattered = %8.5f\n' % self.Tu
        s += 'T_scattered   = %8.5f\n' % self.Td
        s += 'T_total       = %8.5f\n' % (self.Td + self.Tu)
        s += 'Absorbed      = %8.5f\n' % self.absorbed
        s += 'Total         = %8.5f\n' % (self.Rd + self.Ru + self.Td + self.Tu + self.absorbed)
        s += '\n'
        s += 'r_bins = %4d, '   % self.ndr
        s += 'dr = %.3f mm\n' % self.dr
        s += 'z_bins = %4d, '   % self.ndz
        s += 'dz = %.3f mm\n' % self.dz
        return s

    def add_plot_text(self, top=0.98):
        """
        Placeholder to be overridden.
        """
        top = top / 2

    def plot_reflectance(self):
        """
        Plots the radial distribution of diffuse reflectance.

        This method generates a plot of the diffuse reflected excitance (W/mm²)
        as a function of the radius from the center of the incident light.
        The reflectance data (`Rdr`) and the corresponding
        radial positions (`r`) are used to create the plot.

        After calling, follow with plt.show()
        """
        if self.Rdr is None or len(self.Rdr) == 0:
            print('No valid reflection array')
            return

        plt.figure(figsize=(8, 4.5))
        tmp = -self.r[1:]
        r = np.concatenate((tmp[::-1], self.r))
        tmp = self.Rdr[1:]
        refl = np.concatenate((tmp[::-1], self.Rdr))
        plt.plot(r, refl, 'ob', markersize=2)
        plt.xlabel("Radius (mm)")
        plt.ylabel("Reflected Excitance (W/mm²)")
        plt.title('1W incident beam')
        self.add_plot_text()

    def plot_transmittance(self):
        """
        Plots the radial distribution of total transmission.

        This method generates a plot of the transmitted excitance (W/mm²)
        as a function of the radius from the center of the incident light.
        The reflectance data (`Rdr`) and the corresponding
        radial positions (`r`) are used to create the plot.

        After calling, follow with plt.show()
        """
        if self.Ttr is None or len(self.Ttr) == 0:
            print('No valid transmission array')
            return
        plt.figure(figsize=(8, 4.5))
        tmp = -self.r[1:]
        r = np.concatenate((tmp[::-1], self.r))
        tmp = self.Ttr[1:]
        trans = np.concatenate((tmp[::-1], self.Ttr))
        plt.plot(r, trans, 'ob', markersize=2)
        plt.xlabel("Radius (mm)")
        plt.ylabel("Transmitted Excitance (W/mm²)")
        plt.title('1W incident beam')
        self.add_plot_text()

    def plot_1D_z_fluence(self):
        """
        Plots the radial distribution of total transmission.

        This method generates a plot of the fluence (W/mm²)
        as a function of the depth.
        """
        if self.Arz is None or len(self.Arz) == 0:
            print('No valid Arz array')
            return
            
        plt.figure(figsize=(8, 4.5))
        z = self.z[:]
        fluence = self.Arz[0,:].flatten()
        plt.plot(z, fluence, 'ob', markersize=2)
        plt.xlabel("Depth (mm)")
        plt.ylabel("Fluence (W/mm²)")
        plt.title('1W incident beam')
        self.add_plot_text()

    def plot_fluence(self, min_val=1e-8):
        def fmt(x, pos):  # used to label colorbar
            return r'$10^{%g}$' % x

        if self.Arz is None or len(self.Arz) == 0:
            print('No valid Arz absorption matrix')
            return

        rows, cols = self.Arz.shape
        # handle 1D cases
        if cols==1:
            self.plot_1D_z_fluence()
            return

        if rows==1:
            print('Fluence only has one row')
            return

        r_reversed = -self.r[1:-1]
        r = np.concatenate((r_reversed[::-1], self.r[:-1]))
        extent = [-r[-1], r[-1], self.z[-1], 0]

        F = self.Arz[:-1, :-1]
        F_reversed = F[:, 1:]
        F = np.hstack((F_reversed[:, ::-1], F))
        logF = np.log10(F)
        zmin = np.log10(min_val)
        zmax = np.max(logF)
        masked = np.ma.masked_less(logF, zmin)

        cmap = cm.get_cmap('gist_ncar')
        cmap.set_bad(color='black')  # Set the color for masked values

        _, ax = plt.subplots(figsize=(8, 4.5))  # Create a figure and an axes
        im = ax.imshow(masked, extent=extent, aspect='auto', cmap=cmap, \
                       interpolation='none', norm=colors.Normalize(vmin=zmin, vmax=zmax))
        plt.title('Fluence Rate [W/mm²]')
        plt.xlabel('r (mm)')
        plt.ylabel('z (mm)')
        plt.ylim(self.z.max(), -0.1 * self.z.max())
        self.add_plot_text(0.9)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="3%", pad=0.05)
        cbar = plt.colorbar(im, cax=cax)  # Create a colorbar in the specified axes
        cbar.formatter = FuncFormatter(fmt)
        cbar.update_ticks()
        plt.show()

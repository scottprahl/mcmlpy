mcmlpy
======

by Scott Prahl

.. image:: https://img.shields.io/pypi/v/mcmlpy?color=68CA66
   :target: https://pypi.org/project/mcmlpy/
   :alt: pypi

.. image:: https://img.shields.io/github/v/tag/scottprahl/mcmlpy?label=github&color=68CA66
   :target: https://github.com/scottprahl/mcmlpy
   :alt: github

.. image:: https://img.shields.io/conda/vn/conda-forge/mcmlpy?label=conda&color=68CA66
   :target: https://github.com/conda-forge/mcmlpy-feedstock
   :alt: conda

.. image:: https://zenodo.org/badge/116033943.svg
   :target: https://zenodo.org/badge/latestdoi/116033943
   :alt: doi  

|

.. image:: https://img.shields.io/github/license/scottprahl/mcmlpy?color=68CA66
   :target: https://github.com/scottprahl/mcmlpy/blob/main/LICENSE.txt
   :alt: License

.. image:: https://github.com/scottprahl/mcmlpy/actions/workflows/test.yaml/badge.svg
   :target: https://github.com/scottprahl/mcmlpy/actions/workflows/test.yaml
   :alt: Testing

.. image:: https://readthedocs.org/projects/mcmlpy/badge?color=68CA66
   :target: https://mcmlpy.readthedocs.io
   :alt: Docs

.. image:: https://img.shields.io/pypi/dm/mcmlpy?color=68CA66
   :target: https://pypi.org/project/mcmlpy/
   :alt: Downloads

__________

A basic collection of routines to ray trace through graded index (GRIN) lenses with a
parabolic radial profile.

.. image:: https://raw.githubusercontent.com/scottprahl/mcmlpy/main/docs/pitch.png
   :alt: full pitch lens

Example
-------

Properties of a 0.25 pitch GRIN lens from an ancient Melles Griot Catalog::

    import mcmlpy
    n = 1.608 
    gradient = 0.339 
    length = 5.37
    diameter = 1.8
    
    pitch = mcmlpy.period(gradient, length)
    ffl = mcmlpy.FFL(n,pitch,length)
    efl = mcmlpy.EFL(n,pitch,length)
    na = mcmlpy.NA(n,pitch,length,diameter)

    angle = mcmlpy.max_angle(n,pitch,length,diameter)
    print('expected pitch = 0.29,            calculated %.2f' % pitch)
    print('expected FFL = 0.46 mm,           calculated %.2f' % ffl)
    print('expected NA = 0.46,               calculated %.2f' % na)
    print('expected full accept angle = 55°, calculated %.0f°' % (2*angle*180/np.pi))
    print('working distance = %.2f mm'%(efl-ffl))

Produces::

    expected pitch = 0.29,            calculated 0.29
    expected FFL = 0.46,              calculated 0.47
    expected NA = 0.46,               calculated 0.46
    expected full accept angle = 55°, calculated 55°
    working distance = 1.43 mm

But the real utility of this module is creating plots that show the path of rays through
a GRIN lens.   For examples, see <https://mcmlpy.readthedocs.io>

Installation
------------

Use ``pip``::

    pip install mcmlpy

or ``conda``::

    conda install -c conda-forge mcmlpy

or use immediately by clicking the Google Colaboratory button below

.. image:: https://colab.research.google.com/assets/colab-badge.svg
  :target: https://colab.research.google.com/github/scottprahl/mcmlpy/blob/main
  :alt: Colab

License
-------
``mcmlpy`` is licensed under the terms of the MIT license.
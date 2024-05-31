# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string

from io import StringIO
import pytest
import numpy as np
from mcmlpy import MCMLV1

layers_text = """
3                        # Number of layers
#n   mua  mus   g   d    # One line for each layer
1.0                      # refractive index of medium above
1.5  0.0  0.0  0.0  0.1  # layer 1
1.4  0.1  9.9  0.0  1.0  # layer 2
1.5  0.0  0.0  0.0  0.1  # layer 3
1.0                      # refractive index of medium below
end #of layers
"""

def TestInitialization():
    MCMLV1()

def test_read_layers():
    mcml = MCMLV1()
    fp = StringIO(layers_text)
    mcml.read_layers(fp)

    assert mcml.num_layers == 3
    assert mcml.n_above == 1
    assert mcml.n_below == 1
    assert np.array_equal(mcml.d, [1.0, 10, 1.0])
    assert np.array_equal(mcml.mu_a, [0.0, 0.01, 0.0])
    assert np.array_equal(mcml.mu_s, [0.0, 0.99, 0.0])  # per mm conversion test
    assert np.array_equal(mcml.g, [0.0, 0.0, 0.0])
    assert np.array_equal(mcml.n, [1.5, 1.4, 1.5])

def test_read_file():
    mcml = MCMLV1()
    mcml.init_from_file('mc-lost-v1-1.mco')
    
def test_string():
    mcml = MCMLV1()
    mcml.__str__()
    
if __name__ == "__main__":
    pytest.main()

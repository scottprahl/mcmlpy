# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string

from io import StringIO
import pytest
import numpy as np
from mcmlpy import MCMLV2

layers_text = """# Specify media
#	name		n	mua	mus	g
	air 		1	0	0	0
	water 		1.33	0	0	0
	tissue_1 	1.37	1	100	0.9
	tissue_2 	1.37	1	10	0
	tissue_3 	1.37	2	10	0.7
end #of media

# Specify data for run 1
sample2.mco 	A			# output file name, format.

# 	medium 		thickness
	air
	tissue_1 	0.1
	tissue_2 	0.1
	tissue_3 	0.2
	air
end #of layers
"""

def TestInitialization():
    MCMLV2()

def test_read_layers():
    mcml = MCMLV2()
    fp = StringIO(layers_text)
    mcml.read_layers(fp)

    assert mcml.num_layers == 5
    assert np.array_equal(mcml.layer_name, ['air', 'tissue_1', 'tissue_2', 'tissue_3', 'air'])
    assert np.array_equal(mcml.d, [np.inf, 1.0, 1.0, 2.0, np.inf])
    assert np.array_equal(mcml.mu_a, [0.0, 0.1, 0.1, 0.2, 0.0])
    assert np.array_equal(mcml.mu_s, [0.0, 10, 1, 1, 0.0])  # per mm conversion test
    assert np.array_equal(mcml.g, [0.0, 0.9, 0, 0.7, 0.0])
    assert np.array_equal(mcml.n, [1.0, 1.37, 1.37, 1.37, 1.0])

def test_read_file():
    mcml = MCMLV2()
    mcml.init_from_file('mc-lost-v2-1.mco')
    
if __name__ == "__main__":
    pytest.main()

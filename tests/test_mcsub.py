# pylint: disable=invalid-name
# pylint: disable=too-many-locals
# pylint: disable=too-many-instance-attributes
# pylint: disable=consider-using-f-string

import pytest
from mcmlpy import MCSub

def TestInitialization():
    MCSub()

def test_read_file():
    mcsub = MCSub()
    mcsub.init_from_file('mcOUT1.dat')
    
if __name__ == "__main__":
    pytest.main()

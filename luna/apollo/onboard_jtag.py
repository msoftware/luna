#
# This file is part of LUNA
#
""" JTAG definitions for on-board JTAG devices. """

from .jtag import JTAGDevice


#
# LUNA boards.
#

class LatticeECP5_12F(JTAGDevice):
    """ Class representing a JTAG-connected ECP5. """

    DESCRIPTION = "Lattice LFE5U-12F ECP5 FPGA"
    SUPPORTED_IDCODES = [0x21111043]


#
# Daisho boards.
#

class IntelCycloneIV_EP4CE30(JTAGDevice):
    """ Class representing a JTAG-connected CycloneIV, as on Daisho. """

    DESCRIPTION = "Intel/Altera EP4CE30 Cyclone-IV FPGA"
    SUPPORTED_IDCODES = [0x020f40dd]

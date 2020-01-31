#
# This file is part of LUNA.
#
""" Boilerplate for LUNA unit tests. """

import os
import unittest

from functools import wraps

from nmigen import Signal
from nmigen.test.utils import FHDLTestCase
from nmigen.back.pysim import Simulator


def sync_test_case(process_function, *, domain="sync"):
    """ Decorator that converts a function into a simple synchronous-process test case. """

    #
    # This function should automatically transform a given function into a pysim
    # synch process _without_ losing the function's binding on self. Accordingly,
    # we'll create a wrapper function that has self bound, and then a test case
    # that's closed over that wrapper function's context.
    #
    # This ensure that self is still accessible from the decorated function.
    #

    def run_test(self):
        @wraps(process_function)
        def test_case():
            yield from self.initialize_signals()
            yield from process_function(self)

        self.sim.add_sync_process(test_case, domain=domain)
        self.simulate(vcd_suffix=process_function.__name__)

    return run_test


def ulpi_domain_test_case(process_function):
    """
    Decorator that converts a function into a simple synchronous-process
    test case in the ULPI domain.
    """
    return sync_test_case(process_function, domain='ulpi')


def fast_domain_test_case(process_function):
    """
    Decorator that converts a function into a simple synchronous-process
    test case in the ULPI domain.
    """
    return sync_test_case(process_function, domain='fast')



class LunaGatewareTestCase(FHDLTestCase):

    # Convenience property: if set, instantiate_dut will automatically create
    # the relevant fragment with FRAGMENT_ARGUMENTS.
    FRAGMENT_UNDER_TEST = None
    FRAGMENT_ARGUMENTS = {}

    # Convenience properties: if not None, a clock with the relevant frequency
    # will automatically be added.
    FAST_CLOCK_FREQUENCY = None
    SYNC_CLOCK_FREQUENCY = 120e6
    ULPI_CLOCK_FREQUENCY = None


    def instantiate_dut(self):
        """ Basic-most function to instantiate a device-under-test.

        By default, instantiates FRAGMENT_UNDER_TEST.
        """
        return self.FRAGMENT_UNDER_TEST(**self.FRAGMENT_ARGUMENTS)


    def get_vcd_name(self):
        """ Return the name to use for any VCDs generated by this class. """
        return "test_{}".format(self.__class__.__name__)


    def setUp(self):
        self.dut = self.instantiate_dut()
        self.sim = Simulator(self.dut)

        if self.ULPI_CLOCK_FREQUENCY:
            self.sim.add_clock(1 / self.ULPI_CLOCK_FREQUENCY, domain="ulpi")
        if self.SYNC_CLOCK_FREQUENCY:
            self.sim.add_clock(1 / self.SYNC_CLOCK_FREQUENCY, domain="sync")
        if self.FAST_CLOCK_FREQUENCY:
            self.sim.add_clock(1 / self.FAST_CLOCK_FREQUENCY, domain="fast")



    def initialize_signals(self):
        """ Provide an opportunity for the test apparatus to initialize siganls. """
        yield Signal()


    def traces_of_interest(self):
        """ Returns an interable of traces to include in any generated output. """
        return ()


    def simulate(self, *, vcd_suffix=None):
        """ Runs our core simulation. """

        # If we're generating VCDs, run the test under a VCD writer.
        if os.getenv('GENERATE_VCDS', default=False):

            # Figure out the name of our VCD files...
            vcd_name = self.get_vcd_name()
            if vcd_suffix:
                vcd_name = "{}_{}".format(vcd_name, vcd_suffix)

            # ... and run the simulation while writing them.
            traces = self.traces_of_interest()
            with self.sim.write_vcd(vcd_name + ".vcd", vcd_name + ".gtkw", traces=traces):
                self.sim.run()

        else:
            self.sim.run()


    @staticmethod
    def pulse(signal, *, step_after=True):
        """ Helper method that asserts a signal for a cycle. """
        yield signal.eq(1)
        yield
        yield signal.eq(0)

        if step_after:
            yield


    @staticmethod
    def advance_cycles(cycles):
        """ Helper methods that waits for a given number of cycles. """

        for _ in range(cycles):
            yield


    @staticmethod
    def wait_until(strobe, *, timeout=None):
        """ Helper method that advances time until a strobe signal becomes true. """

        cycles_passed = 0

        while not (yield strobe):
            yield

            cycles_passed += 1
            if timeout and cycles_passed > timeout:
                raise RuntimeError(f"Timeout waiting for '{strobe.name}' to go high!")

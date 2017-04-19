# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2013)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Unit test for signal module
"""

from compat import unittest

import numpy
from numpy import testing as nptest

from scipy import signal

from astropy import units

import lal

from gwpy import signal as gwpy_signal
from gwpy.signal.fft import (lal as fft_lal, utils as fft_utils)

ONE_HZ = units.Quantity(1, 'Hz')

NOTCH_60HZ = (
    numpy.asarray([ 0.99973536+0.02300468j,  0.99973536-0.02300468j]),
    numpy.asarray([ 0.99954635-0.02299956j,  0.99954635+0.02299956j]),
    0.99981094420429639,
)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


# -- gwpy.signal.filter_design ------------------------------------------------

class FilterDesignTestCase(unittest.TestCase):
    """`~unittest.TestCase` for the `gwpy.signal.filter_design` module
    """
    def test_notch_design(self):
        # test simple notch
        zpk = gwpy_signal.notch(60, 16384)
        for a, b in zip(zpk, NOTCH_60HZ):
            nptest.assert_array_almost_equal(a, b)
        # test Quantities
        zpk2 = gwpy_signal.notch(60 * ONE_HZ, 16384 * ONE_HZ)
        for a, b in zip(zpk, zpk2):
            nptest.assert_array_almost_equal(a, b)


# -- gwpy.signal.fft.utils ----------------------------------------------------

class FFTUtilsTests(unittest.TestCase):
    def test_scale_timeseries_units(self):
        u = units.Unit('m')
        # check default
        self.assertEqual(fft_utils.scale_timeseries_units(u),
                         units.Unit('m^2/Hz'))
        # check scaling='density'
        self.assertEqual(
            fft_utils.scale_timeseries_units(u, scaling='density'),
            units.Unit('m^2/Hz'))
        # check scaling='spectrum'
        self.assertEqual(
            fft_utils.scale_timeseries_units(u, scaling='spectrum'),
            units.Unit('m^2'))
        # check anything else raises an exception
        self.assertRaises(ValueError, fft_utils.scale_timeseries_units,
                          u, scaling='other')
        # check null unit
        self.assertEqual(fft_utils.scale_timeseries_units(None),
                         units.Unit('Hz^-1'))


# -- gwpy.signal.fft.lal ------------------------------------------------------

class LALFftTests(unittest.TestCase):
    def test_generate_window(self):
        # test default arguments
        w = fft_lal.generate_window(128)
        self.assertIsInstance(w, lal.REAL8Window)
        self.assertEqual(w.data.data.size, 128)
        self.assertEqual(w.sum, 32.31817089602309)
        # test generating the same window again returns the same object
        self.assertIs(fft_lal.generate_window(128), w)
        # test dtype works
        w = fft_lal.generate_window(128, dtype='float32')
        self.assertIsInstance(w, lal.REAL4Window)
        self.assertEqual(w.sum, 32.31817089602309)
        # test errors
        self.assertRaises(AttributeError, fft_lal.generate_window,
                          128, 'unknown')
        self.assertRaises(AttributeError, fft_lal.generate_window,
                          128, dtype=int)

    def test_generate_fft_plan(self):
        # test default arguments
        plan = fft_lal.generate_fft_plan(128)
        self.assertIsInstance(plan, lal.REAL8FFTPlan)
        # test generating the same fft_plan again returns the same object
        self.assertIs(fft_lal.generate_fft_plan(128), plan)
        # test dtype works
        plan = fft_lal.generate_fft_plan(128, dtype='float32')
        self.assertIsInstance(plan, lal.REAL4FFTPlan)
        # test forward/backward works
        rvrs = fft_lal.generate_fft_plan(128, forward=False)
        self.assertIsInstance(rvrs, lal.REAL8FFTPlan)
        self.assertIsNot(rvrs, plan)
        # test errors
        self.assertRaises(AttributeError, fft_lal.generate_fft_plan,
                          128, dtype=int)

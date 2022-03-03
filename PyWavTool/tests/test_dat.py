
import unittest
import os
import os.path
import shutil

import numpy as np

import dat

class TestDat(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("writetest.wav.dat")
        except:
            pass
        shutil.rmtree("test_output", ignore_errors=True)

    def test_init(self):
        _dat = dat.Dat(os.path.join("testdata","440.wav.dat"))
        self.assertEqual(len(_dat._data),0)

    def test_no_file(self):
        _dat = dat.Dat(os.path.join("testdata","hoge.wav.dat"))
        self.assertEqual(len(_dat._data),0)

    def test_add_frame(self):
        _dat = dat.Dat(os.path.join("testdata","100.wav.dat"))
        _dat.read(16)
        nframes = _dat.addframe(np.full(44100, 50/32768), 0, 16, 44100)
        self.assertEqual(len(_dat._data), 88200)
        self.assertEqual(nframes, 44100)
        np.testing.assert_array_equal(_dat._data[44050:44100], np.full(50, 100))
        np.testing.assert_array_equal(_dat._data[44100:44150], np.full(50, 50))
        
    def test_add_frame_overlap(self):
        _dat = dat.Dat(os.path.join("testdata","100.wav.dat"))
        _dat.read(16)
        nframes = _dat.addframe(np.full(44100, 50/32768), 500, 16, 44100)
        self.assertEqual(len(_dat._data), 44100 + 22050)
        self.assertEqual(nframes, 22050)
        np.testing.assert_array_equal(_dat._data[22000:22050], np.full(50, 100))
        np.testing.assert_array_equal(_dat._data[22050:22100], np.full(50, 150))
        np.testing.assert_array_equal(_dat._data[44050:44100], np.full(50, 150))
        np.testing.assert_array_equal(_dat._data[44100:44150], np.full(50, 50))

    def test_write(self):
        _dat = dat.Dat(os.path.join("testdata","440.wav.dat"))
        self.assertFalse(os.path.isfile("writetest.wav.dat"))
        _dat.read(16)
        _dat.write("writetest.wav.dat", 16)
        self.assertTrue(os.path.isfile("writetest.wav.dat"))
        _dat2 = dat.Dat("writetest.wav.dat")
        _dat2.read(16)
        np.testing.assert_array_equal(_dat._data, _dat2._data)
        
    def test_write_checkValue(self):
        _dat = dat.Dat(os.path.join("testdata","100.wav.dat"))
        self.assertFalse(os.path.isfile("writetest.wav.dat"))
        shutil.copy(os.path.join("testdata","100.wav.dat"),"writetest.wav.dat")
        _dat2 = dat.Dat("writetest.wav.dat")
        _dat2.read(16)
        self.assertEqual(_dat2._data.shape[0], 44100)
        nframes = _dat.addframeAndWrite(np.full(44100, 50/32768), 500, 16, 44100, "writetest.wav.dat")
        self.assertTrue(os.path.isfile("writetest.wav.dat"))
        _dat2 = dat.Dat("writetest.wav.dat")
        _dat2.read(16)
        self.assertEqual(_dat2._data.shape[0], 44100 + 22050)
        np.testing.assert_array_equal(_dat2._data[22000:22050], np.full(50, 100))
        np.testing.assert_array_equal(_dat2._data[22050:22100], np.full(50, 150))
        np.testing.assert_array_equal(_dat2._data[44050:44100], np.full(50, 150))
        np.testing.assert_array_equal(_dat2._data[44100:44150], np.full(50, 50))
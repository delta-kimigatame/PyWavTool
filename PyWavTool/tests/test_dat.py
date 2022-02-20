
import unittest
import os
import os.path
import shutil

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
        nframes = _dat.addframe([50/32768]*44100, 0, 16, 44100)
        self.assertEqual(len(_dat._data), 88200)
        self.assertEqual(nframes, 44100)
        self.assertEqual(_dat._data[44050:44150], [100]*50 + [50]*50)
        
    def test_add_frame_overlap(self):
        _dat = dat.Dat(os.path.join("testdata","100.wav.dat"))
        nframes = _dat.addframe([50/32768]*44100, 500, 16, 44100)
        self.assertEqual(len(_dat._data), 44100 + 22050)
        self.assertEqual(nframes, 22050)
        self.assertEqual(_dat._data[22001:22101], [100]*50 + [150]*50)
        self.assertEqual(_dat._data[44050:44150], [150]*50 + [50]*50)

    def test_write(self):
        _dat = dat.Dat(os.path.join("testdata","440.wav.dat"))
        self.assertFalse(os.path.isfile("writetest.wav.dat"))
        _dat.write("writetest.wav.dat", 16)
        self.assertTrue(os.path.isfile("writetest.wav.dat"))
        _dat2 = dat.Dat("writetest.wav.dat")
        self.assertEqual(_dat._data,_dat2._data)
        
    def test_write_checkValue(self):
        _dat = dat.Dat(os.path.join("testdata","100.wav.dat"))
        self.assertFalse(os.path.isfile("writetest.wav.dat"))
        shutil.copy(os.path.join("testdata","100.wav.dat"),"writetest.wav.dat")
        _dat2 = dat.Dat("writetest.wav.dat")
        _dat2.read(16)
        self.assertEqual(len(_dat2._data), 44100)
        nframes = _dat.addframeAndWrite([50/32768]*44100, 500, 16, 44100, "writetest.wav.dat")
        self.assertTrue(os.path.isfile("writetest.wav.dat"))
        _dat2 = dat.Dat("writetest.wav.dat")
        _dat2.read(16)
        self.assertEqual(len(_dat2._data), 44100 + 22050)
        self.assertEqual(_dat2._data[22000:22100], [100]*50 + [150]*50)
        self.assertEqual(_dat2._data[44050:44150], [150]*50 + [50]*50)
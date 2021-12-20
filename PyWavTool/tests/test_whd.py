
import unittest
import os
import os.path
import shutil

import whd

class TestWhd(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("writetest.wav.whd")
        except:
            pass
        shutil.rmtree("test_output", ignore_errors=True)

    def test_InitWhd(self):
        head=whd.Whd()
        self.assertEqual(head.nchannels, 1)
        self.assertEqual(head.framerate, 44100)
        self.assertEqual(head.samplewidth,16)
        self.assertEqual(head.nframes,0)

    def test_WriteWhd(self):
        head=whd.Whd()
        self.assertFalse(os.path.isfile("writetest.wav.whd"))
        head.write("writetest.wav")
        self.assertTrue(os.path.isfile("writetest.wav.whd"))
        
    def test_WriteWhd_NoDir(self):
        head=whd.Whd()
        self.assertFalse(os.path.isfile(os.path.join("test_output","writetest.wav.whd")))
        head.write(os.path.join("test_output","writetest.wav"))
        self.assertTrue(os.path.isfile(os.path.join("test_output","writetest.wav.whd")))

    def test_Read(self):
        head=whd.Whd(os.path.join("testdata","440.wav.whd"))
        self.assertEqual(head.nchannels, 1)
        self.assertEqual(head.framerate, 44100)
        self.assertEqual(head.samplewidth,16)
        self.assertEqual(head.nframes,44100)

    def test_Add(self):
        head=whd.Whd()
        self.assertEqual(head.nchannels, 1)
        self.assertEqual(head.framerate, 44100)
        self.assertEqual(head.samplewidth,16)
        self.assertEqual(head.nframes,0)
        head.addframes(44100)
        self.assertEqual(head.nchannels, 1)
        self.assertEqual(head.framerate, 44100)
        self.assertEqual(head.samplewidth,16)
        self.assertEqual(head.nframes,44100)

class TestOutputWhdRead(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("writereadtest.wav.whd")
        except:
            pass
        head=whd.Whd()
        head.addframes(44100)
        head.write("writereadtest.wav")

    def test_ReadOutputData(self):
        head=whd.Whd("writereadtest.wav.whd")
        self.assertEqual(head.nchannels, 1)
        self.assertEqual(head.framerate, 44100)
        self.assertEqual(head.samplewidth,16)
        self.assertEqual(head.nframes,44100)
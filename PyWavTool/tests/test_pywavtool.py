
import unittest
import os
import os.path
import shutil

import PyWavTool

class TestPyWavTool(unittest.TestCase):
    def test_envelope_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500,[0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500, [0, 5, 30, 0, 100, 100, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500, [0, 5, 30, 0, 100, 100, 0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500, [0, 5, 30, 0, 100, 100, 0, 0 ,0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500, [0, 5, 30, 0, 100, 100, 0, 0 ,0, 10, 100])
        self.assertFalse(wavtool.error)

    def test_envelope_not_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500,[0, 0, 0])
        self.assertTrue(wavtool.error)

    def test_input_wav_not_exist(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "hoge.wav"), 0, 500,[0, 0])
        self.assertTrue(wavtool.error)
        
    def test_input_wav_is_not_wav(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "test.txt"), 0, 500,[0, 0])
        self.assertTrue(wavtool.error)

    def test_make_outputdir(self):
        shutil.rmtree(os.path.join("makedir_test"), ignore_errors=True)
        self.assertFalse(os.path.isdir(os.path.join("makedir_test")))
        wavtool=PyWavTool.WavTool(os.path.join("makedir_test", "test.wav"), os.path.join("testdata", "440.wav"), 0, 500,[0, 0])
        self.assertTrue(os.path.isdir(os.path.join("makedir_test")))

import unittest
import os
import os.path
import shutil

import PyWavTool

class TestPyWavToolInput(unittest.TestCase):
    def test_envelope_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0, 0 ,0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0, 0 ,0, 10, 100])
        self.assertFalse(wavtool.error)

    def test_envelope_not_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        wavtool.setEnvelope([0, 0, 0])
        self.assertTrue(wavtool.error)

    def test_input_wav_not_exist(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "hoge.wav"))
        self.assertTrue(wavtool.error)
        
    def test_input_wav_is_not_wav(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "test.txt"))
        self.assertTrue(wavtool.error)

    def test_make_outputdir(self):
        shutil.rmtree(os.path.join("makedir_test"), ignore_errors=True)
        self.assertFalse(os.path.isdir(os.path.join("makedir_test")))
        wavtool=PyWavTool.WavTool(os.path.join("makedir_test", "test.wav"))
        wavtool.inputCheck(os.path.join("testdata", "440.wav"))
        self.assertTrue(os.path.isdir(os.path.join("makedir_test")))

class TestPyWavToolMain(unittest.TestCase):
    def setUp(self):
        self.wavtool = PyWavTool.WavTool(os.path.join("test_output", "test.wav"))
        self.wavtool.inputCheck(os.path.join("testdata", "440.wav"))

    def test_convert_data(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0])
        self.wavtool.applyData(0, 500)
        self.assertEqual(self.wavtool._data[0], 0)
        self.assertEqual(44100, len(self.wavtool._data))
        
    def test_apply_cut(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0])
        self.wavtool.applyData(0, 500)
        self.assertEqual(44100, len(self.wavtool._data))
        self.assertEqual(44100/2, len(self.wavtool._range_data))
        
    def test_apply_stp(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 100, 0])
        self.wavtool.applyData(500, 500)
        self.assertEqual(44100, len(self.wavtool._data))
        self.assertEqual(44100/2, len(self.wavtool._range_data))
        self.assertEqual(self.wavtool._data[22050], self.wavtool._range_data[0])

    def test_apply_envelope_2(self):
        self.wavtool.setEnvelope([0, 0])
        self.wavtool.applyData(0, 500)
        self.assertEqual(44100/2, len(self.wavtool._apply_data))
        self.assertEqual([0]*22050, self.wavtool._apply_data)

    def test_apply_envelope_no_change(self):
        self.wavtool.setEnvelope([0, 5, 30, 100, 100, 100, 100])
        self.wavtool.applyData(0, 500)
        self.assertEqual(44100/2, len(self.wavtool._apply_data))
        self.assertEqual(self.wavtool._range_data, self.wavtool._apply_data)

    def test_apply_envelope_default(self):
        self.wavtool.setEnvelope([0, 5, 30, 100, 100, 100, 100])
        self.wavtool.applyData(0, 500)
        self.wavtool._range_data=[1]*100
        self.wavtool._applyEnvelope([0,0,5,70,100], [0,0,100,100,0])
        self.assertEqual(self.wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(self.wavtool._apply_data[5:70], [1]*65)
        self.assertEqual(self.wavtool._apply_data[71], 1-1/30)
        
    def test_apply_envelope4_2(self):
        self.wavtool.setEnvelope([0, 5, 30, 100, 100, 100, 100])
        self.wavtool.applyData(0, 500)
        self.wavtool._range_data=[1]*100
        self.wavtool._applyEnvelope([0,0,5,10,100], [0,0,100,90,0])
        self.assertEqual(self.wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(self.wavtool._apply_data[5:10], [1.00, 0.98,0.96,0.94, 0.92])
        
    def test_apply_envelope4_samepoint(self):
        self.wavtool.setEnvelope([0, 5, 30, 100, 100, 100, 100])
        self.wavtool.applyData(0, 500)
        self.wavtool._range_data=[1]*100
        self.wavtool._applyEnvelope([0,0,5,5,100], [0,0,100,90,0])
        self.assertEqual(self.wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(self.wavtool._apply_data[5], 0.9)

    def test_get_envelope_default(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 150, 0])
        self.wavtool.applyData(0, 500)
        p, v = self.wavtool._getEnvelopes(100)
        self.assertEqual(v, [0, 0, 100, 150, 0, 0])
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*70),  int(44.1*100)])

    def test_get_envelope_9(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 150, 0, 5, 35])
        self.wavtool.applyData(0, 500)
        p, v = self.wavtool._getEnvelopes(100)
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*35), int(44.1*65), int(44.1*100)])
        self.assertEqual(v, [0, 0, 100, 150, 0, 0])

        
    def test_get_envelope_11(self):
        self.wavtool.setEnvelope([0, 5, 30, 0, 100, 150, 0, 5, 35, 5, 80])
        self.wavtool.applyData(0, 500)
        p, v = self.wavtool._getEnvelopes(100)
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*10), int(44.1*35), int(44.1*65), int(44.1*100)])
        self.assertEqual(v, [0, 0, 100, 80, 150, 0, 0])
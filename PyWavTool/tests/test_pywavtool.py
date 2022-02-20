
import unittest
import os
import os.path
import shutil

import PyWavTool

class TestPyWavTool(unittest.TestCase):
    def test_envelope_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0, 0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0, 0 ,0])
        self.assertFalse(wavtool.error)
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0, 0 ,0, 10, 100])
        self.assertFalse(wavtool.error)

    def test_envelope_not_matching(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 0, 0])
        self.assertTrue(wavtool.error)

    def test_input_wav_not_exist(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "hoge.wav"),[0, 0])
        self.assertTrue(wavtool.error)
        
    def test_input_wav_is_not_wav(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "test.txt"),[0, 0])
        self.assertTrue(wavtool.error)

    def test_make_outputdir(self):
        shutil.rmtree(os.path.join("makedir_test"), ignore_errors=True)
        self.assertFalse(os.path.isdir(os.path.join("makedir_test")))
        wavtool=PyWavTool.WavTool(os.path.join("makedir_test", "test.wav"), os.path.join("testdata", "440.wav"),[0, 0])
        self.assertTrue(os.path.isdir(os.path.join("makedir_test")))

    def test_convert_data(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0])
        wavtool.applyData(0, 500)
        self.assertEqual(wavtool._data[0], 0)
        self.assertEqual(44100, len(wavtool._data))
        
    def test_apply_cut(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0])
        wavtool.applyData(0, 500)
        self.assertEqual(44100, len(wavtool._data))
        self.assertEqual(44100/2, len(wavtool._range_data))
        
    def test_apply_stp(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 100, 0])
        wavtool.applyData(500, 500)
        self.assertEqual(44100, len(wavtool._data))
        self.assertEqual(44100/2, len(wavtool._range_data))
        self.assertEqual(wavtool._data[22050], wavtool._range_data[0])

    def test_apply_envelope_2(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 0])
        wavtool.applyData(0, 500)
        self.assertEqual(44100/2, len(wavtool._apply_data))
        self.assertEqual([0]*22050, wavtool._apply_data)

    def test_apply_envelope_no_change(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 5, 30, 100, 100, 100, 100])
        wavtool.applyData(0, 500)
        self.assertEqual(44100/2, len(wavtool._apply_data))
        self.assertEqual(wavtool._range_data, wavtool._apply_data)

    def test_apply_envelope_default(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 5, 30, 100, 100, 100, 100])
        wavtool.applyData(0, 500)
        wavtool._range_data=[1]*100
        wavtool._applyEnvelope([0,0,5,70,100], [0,0,100,100,0])
        self.assertEqual(wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(wavtool._apply_data[5:70], [1]*65)
        self.assertEqual(wavtool._apply_data[71], 1-1/30)
        
    def test_apply_envelope4_2(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 5, 30, 100, 100, 100, 100])
        wavtool.applyData(0, 500)
        wavtool._range_data=[1]*100
        wavtool._applyEnvelope([0,0,5,10,100], [0,0,100,90,0])
        self.assertEqual(wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(wavtool._apply_data[5:10], [1.00, 0.98,0.96,0.94, 0.92])
        
    def test_apply_envelope4_samepoint(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"),[0, 5, 30, 100, 100, 100, 100])
        wavtool.applyData(0, 500)
        wavtool._range_data=[1]*100
        wavtool._applyEnvelope([0,0,5,5,100], [0,0,100,90,0])
        self.assertEqual(wavtool._apply_data[0:5], [0,0.2,0.4,0.6,0.8])
        self.assertEqual(wavtool._apply_data[5], 0.9)

    def test_get_envelope_default(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 150, 0])
        wavtool.applyData(0, 500)
        p, v = wavtool._getEnvelopes(100)
        self.assertEqual(v, [0, 0, 100, 150, 0, 0])
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*70),  int(44.1*100)])

    def test_get_envelope_9(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 150, 0, 5, 35])
        wavtool.applyData(0, 500)
        p, v = wavtool._getEnvelopes(100)
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*35), int(44.1*65), int(44.1*100)])
        self.assertEqual(v, [0, 0, 100, 150, 0, 0])

        
    def test_get_envelope_11(self):
        wavtool=PyWavTool.WavTool(os.path.join("test_output", "test.wav"), os.path.join("testdata", "440.wav"), [0, 5, 30, 0, 100, 150, 0, 5, 35, 5, 80])
        wavtool.applyData(0, 500)
        p, v = wavtool._getEnvelopes(100)
        self.assertEqual(p, [0, 0, int(44.1*5), int(44.1*10), int(44.1*35), int(44.1*65), int(44.1*100)])
        self.assertEqual(v, [0, 0, 100, 80, 150, 0, 0])
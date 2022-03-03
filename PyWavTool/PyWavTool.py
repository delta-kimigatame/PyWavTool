import sys
import os
import os.path
import wave
import argparse
import math
from typing import Tuple

import numpy as np

sys.path.append(os.path.dirname(__file__)) #embeddable pythonにimpot用のパスを追加
import whd
import dat
import length_string

ARROW_ENVELOPE_VALUES = [2, 7, 8, 9, 11]


class WavTool:
    '''
    | WavToolはUTAU標準のwavtoolをエミュレートします。
    | wavを入力し、waveヘッダ(.wav.whd)とwaveデータ(.wav.dat)を出力します。
    | すでにwhdとdatがある場合、datの末尾にデータを加え、whdを更新します。

    Attributes
    ----------
    ourput : str
        出力するwavのパス
    input : str
        入力するwavのパス
    stp : float
        入力wavの先頭のオフセットをmsで指定する。
    length : float
        datに追加する長さ(ms)
    envelope : list
        エンベロープのパターンは以下のいずれかです。
            >>> p1 p2
            >>> p1 p2 p3 v1 v2 v3 v4
            >>> p1 p2 p3 v1 v2 v3 v4 ove
            >>> p1 p2 p3 v1 v2 v3 v4 ove p4
            >>> p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
        | p1,p2,p3,p4,p5,ove : float
        | v1,v2,v3,v4,v5 : int
    header : whd.Whd
        .whdファイルを扱います。
    dat : dat.Dat
        .datファイルを扱います。
    '''
    _error: bool = False
    _output: str
    _input: str
    _stp: float
    _length: float
    _data: np.ndarray
    _range_data: np.ndarray
    _apply_data: np.ndarray
    _header: whd.Whd
    _dat: dat.Dat

    @property
    def error(self) -> bool:
        return self._error

    def __init__(self, output: str):
        '''
        Parameters
        ----------
        ourput : str
            出力するwavのパス
        '''
        self._error = False
        if os.path.split(output)[0] != "":
            os.makedirs(os.path.split(output)[0], exist_ok=True)
        self._header = whd.Whd(output + ".whd")
        self._dat = dat.Dat(output + ".dat")
        self._output = output
            
    def applyData(self,stp: float,length: float):
        '''
        Parameters
        ----------
        stp : float
            入力wavの先頭のオフセットをmsで指定する。
        length : float
            datに追加する長さ(ms)
        '''
        ove :float
        if len(self._envelope) >= 8:
            ove = self._envelope[7]
        else:
            ove = 0

        if not self._error:
            self._applyRange(stp, length)
            p, v = self._getEnvelopes(length)
            self._applyEnvelope(p, v)
        else:
            self._apply_data = np.zeros(math.ceil(length * self._header.framerate / 1000))
        nframes: int = self._dat.addframeAndWrite(self._apply_data, ove, self._header.samplewidth, self._header.framerate,self._output + ".dat")
        self._header.addframes(nframes)


    def inputCheck(self, input:str):
        '''
        | 入力値が正しいかチェックします。
        | 正常値の場合、self._dataにwavの中身を最大1に正規化したfloatに変換して代入します。
        | 異常値の場合、self._errorをTrueにします。

        Parameters
        ----------
        input : str
            入力するwavのパス
        '''
        self._error = False

        basedata :list
        if (not os.path.isfile(input)):
            print("input file is not found:{}".format(input))
            self._error = True
            return
        try:
            with wave.open(input,"rb") as wr:
                basedata = wr.readframes(wr.getnframes())
                samplewidth :int = wr.getsampwidth()
        except:
            print("file format error:{} is not wave.".format(input))
            self._error = True
            return
        if samplewidth == 1:
            data: np.ndarray = np.frombuffer(basedata, dtype=np.int8)
        elif samplewidth == 2:
            data: np.ndarray = np.frombuffer(basedata, dtype=np.int16)
        elif samplewidth == 3:
            data: np.ndarray = np.zeros(int(len(basedata)/3), dtype = "int32")
            for i in range(self._data.shape[0]):
                data[i] = int.from_bytes(basedata[i*3:(i+1)*3], "little", signed=True)
        elif samplewidth == 4:
            data: np.ndarray = np.frombuffer(basedata, dtype=np.int32)

        self._data = data.astype(np.float64)
        self._data /= (2 ** (samplewidth *8) /2) #正規化

    def setEnvelope(self, envelope: list):
        '''
        | 入力されたエンベロープが正しいかチェックします。
        | 正常値であれば、self._envelopeを更新します。
        | 異常値であれば、self._ErrorをTrueにします。

        Parameters
        ----------
        envelope : list
            エンベロープのパターンは以下のいずれかです。
                p1 p2
                p1 p2 p3 v1 v2 v3 v4
                p1 p2 p3 v1 v2 v3 v4 ove
                p1 p2 p3 v1 v2 v3 v4 ove p4
                p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
            p1,p2,p3,p4,p5,ove : float
            v1,v2,v3,v4,v5 : int
        '''
        if (len(envelope) in ARROW_ENVELOPE_VALUES):
            # エンベロープがパターンにマッチしているか確認
            self._envelope = envelope
        else:
            print("value error:envelope patern is not matching.")
            self._error = True


    def _applyRange(self, stp:float, length :float):
        '''
        | stpを適用し、self._range_dataを返します。
        | 事前にself._dataに最大1に正規化したwavデータが格納されていることが条件です。

        Parameters
        ----------
        stp : float
            入力wavの先頭のオフセットをmsで指定する。
        length : float
            datに追加する長さ(ms)
        '''
        stp_frames = int(stp * self._header.framerate / 1000)
        length_frames = int(length * self._header.framerate / 1000)
        self._range_data:np.ndarray = self._data[stp_frames:stp_frames + length_frames]

    def _applyEnvelope(self, p :list, v :list):
        '''
        | エンベロープ・stpを適用し、self._apply_dataを返します。
        | 事前にself._range_dataに最大1に正規化したwavデータが格納されていることが条件です。

        Parameters
        ----------
        p :list of float
            Pstart P1 P2 P3 (P5) P4 Pendの順に並べたポルタメント。エンベロープが2点の場合空配列
        v: list of int
            ノート頭からms順に並べたポルタメントの音量値。エンベロープが2点の場合空配列
        '''

        if len(p) == 0: #休符等の例外
            self._apply_data = np.zeros_like(self._range_data)
            return

        self._apply_data = self._range_data * np.interp(np.arange(self._range_data.shape[0]), p, v[:len(p)]) / 100

    def _getEnvelopes(self, length: float) -> Tuple[list, list]:
        '''
        | エンベロープをノート頭からのms順に並べ、pとvのリストを返します。
        | エンベロープがパターンにマッチすることを事前に確認するのが条件です。
        Parameters
        ----------
        length : float
            datに追加する長さ(ms)

        Returns
        -------
        p :list of int
            Pstart P1 P2 P3 (P5) P4 Pendの順に並べたポルタメント。エンベロープが2点の場合空配列
        v: list of int
            ノート頭からms順に並べたポルタメントの音量値。エンベロープが2点の場合空配列
        '''
        
        if len(self._envelope) == 2: #休符等の例外
            return [], []

        p :list = [0] #Pstart
        v :list = [0] #Vstart
        frame_per_ms: float = self._header.framerate / 1000
        p.append(int(float(self._envelope[0]) * frame_per_ms)) #p1
        p.append(int((float(self._envelope[0]) + float(self._envelope[1])) * frame_per_ms)) #p2
        v.append(int(self._envelope[3])) #v1
        v.append(int(self._envelope[4])) #v2
        if len(self._envelope) >= 11:
            p.append(int((float(self._envelope[0]) + float(self._envelope[1]) + float(self._envelope[9])) * frame_per_ms)) #p5
            v.append(int(self._envelope[10])) #v5
        v.append(int(self._envelope[5])) #v3
        v.append(int(self._envelope[6])) #v4
        if len(self._envelope) >= 9:
            p.append(int((length - float(self._envelope[8]) - float(self._envelope[2])) * frame_per_ms))  #p3はp4からのms
            p.append(int((length - float(self._envelope[8])) * frame_per_ms)) #p4は後ろからのms
        else:
            p.append(int((length - float(self._envelope[2])) * frame_per_ms)) #p3はp4からのms

        p.append(length * frame_per_ms) # Pend
        v.append(0) #Vend

        return p,v

    def write(self):
        self._header.write(self._output)
        #self._dat.write(self._output + ".dat", self._header.samplewidth)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This module emulate UTAU\'s wavtool')
    parser.add_argument('output', help='output wav path', type=str)
    parser.add_argument('input', help='input wav path', type=str)
    parser.add_argument('stp', help='start offset of wav', type=float)
    parser.add_argument('length', help='append length(ms)')
    parser.add_argument('envelope', nargs='*', type=float,
                        help='envelope patern ' +
                        '\'p1 p2\' or \'p1 p2 p3 v1 v2 v3 v4 ove\'' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5\'')
    args = parser.parse_args()
    if (len(args.envelope) not in ARROW_ENVELOPE_VALUES):
        print("value error:envelope patern is not matching.")
    length: float
    wavtool = WavTool(args.output)
    wavtool.inputCheck(args.input)
    wavtool.setEnvelope(args.envelope)
    if type(args.length) == float:
        length = args.length
    else:
        length = length_string.str2float(args.length)
    wavtool.applyData(args.stp, length)
    wavtool.write()

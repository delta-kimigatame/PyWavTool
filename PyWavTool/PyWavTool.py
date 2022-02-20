
import os
import os.path
import wave
import argparse
from typing import Tuple

import whd
import dat

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
    '''
    _error: bool = False
    _output: str
    _input: str
    _stp: float
    _length: float
    _data: list
    _range_data :list
    _apply_data :list
    _header: whd.Whd

    @property
    def error(self) -> bool:
        return self._error

    def __init__(self,
                 output: str,
                 input: str,
                 stp: float,
                 length: float,
                 envelope: list):
        '''
        Parameters
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
                p1 p2
                p1 p2 p3 v1 v2 v3 v4
                p1 p2 p3 v1 v2 v3 v4 ove
                p1 p2 p3 v1 v2 v3 v4 ove p4
                p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
            p1,p2,p3,p4,p5,ove : float
            v1,v2,v3,v4,v5 : int
        '''
        ove :float
        self._error = False
        self._inputCheck(input, envelope)
        os.makedirs(os.path.split(output)[0], exist_ok=True)
        self._header = whd.Whd(output + ".whd")
        self._dat = dat.Dat(output + ".dat", self._header.samplewidth)
        if len(envelope) >= 8:
            ove = envelope[7]
        else:
            ove = 0

        if not self._error:
            self._applyRange(stp, length)
            p, v = self._getEnvelopes(envelope, length)
            self._applyEnvelope(p, v)
            nframes: int = self._dat.addframe(self._apply_data, ove, self._header.samplewidth, self._header.framerate)
            self._header.addframes(nframes)
            


    def _inputCheck(self, input:str ,envelope: list):
        '''
        | 入力値が正しいかチェックします。
        | 正常値の場合、self._dataにwavの中身を最大1に正規化したfloatに変換して代入します。
        | 異常値の場合、self._errorをTrueにします。

        Parameters
        ----------
        input : str
            入力するwavのパス
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

        basedata :list
        data :list =[]
        self._data = []
        if (len(envelope) not in ARROW_ENVELOPE_VALUES):
            # エンベロープがパターンにマッチしているか確認
            print("value error:envelope patern is not matching.")
            self._error = True
            return
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
        for i in range(int(len(basedata)/samplewidth)):#byteからintに変換。
            data.append(int.from_bytes(basedata[i*samplewidth:(i+1)*samplewidth], 'little', signed=True))
        self._data = list(map(lambda i:i / (2 ** (samplewidth * 8) /2), data)) #正規化

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
        self._range_data = self._data[stp_frames:stp_frames + length_frames]

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
            self._apply_data = [0] * len(self._range_data)
            return

        self._apply_data = []
        pos: int = 0
        while p[pos] == p[pos+1]:
            pos = pos + 1
            if pos >= len(p):
                break
        delta:float = (v[pos+1] - v[pos]) / (p[pos+1] - p[pos])
        for i in range(len(self._range_data)):
            if i >= p[pos + 1]:
                pos = pos +1
                while p[pos] == p[pos+1]:
                    pos = pos + 1
                    if pos >= len(p):
                        break
                delta = (v[pos+1] - v[pos]) / (p[pos+1] - p[pos])
            self._apply_data.append((v[pos] + delta * (i - p[pos])) / 100 * self._range_data[i])

    def _getEnvelopes(self, envelope: list, length: float) -> Tuple[list, list]:
        '''
        | エンベロープをノート頭からのms順に並べ、pとvのリストを返します。
        | エンベロープがパターンにマッチすることを事前に確認するのが条件です。
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
        length : float
            datに追加する長さ(ms)

        Returns
        -------
        p :list of int
            Pstart P1 P2 P3 (P5) P4 Pendの順に並べたポルタメント。エンベロープが2点の場合空配列
        v: list of int
            ノート頭からms順に並べたポルタメントの音量値。エンベロープが2点の場合空配列
        '''
        
        if len(envelope) == 2: #休符等の例外
            return [], []

        p :list = [0] #Pstart
        v :list = [0] #Vstart
        frame_per_ms: float = self._header.framerate / 1000
        p.append(int(float(envelope[0]) * frame_per_ms)) #p1
        p.append(int((float(envelope[0]) + float(envelope[1])) * frame_per_ms)) #p2
        v.append(int(envelope[3])) #v1
        v.append(int(envelope[4])) #v2
        if len(envelope) >= 11:
            p.append(int((float(envelope[0]) + float(envelope[1]) + float(envelope[9])) * frame_per_ms)) #p5
            v.append(int(envelope[10])) #v5
        v.append(int(envelope[5])) #v3
        v.append(int(envelope[6])) #v4
        if len(envelope) >= 9:
            p.append(int((length - float(envelope[8]) - float(envelope[2])) * frame_per_ms))  #p3はp4からのms
            p.append(int((length - float(envelope[8])) * frame_per_ms)) #p4は後ろからのms
        else:
            p.append(int((length - float(envelope[2])) * frame_per_ms)) #p3はp4からのms

        p.append(length * frame_per_ms) # Pend
        v.append(0) #Vend

        return p,v


        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This module emulate UTAU\'s wavtool')
    parser.add_argument('output', help='output wav path', type=str)
    parser.add_argument('input', help='input wav path', type=str)
    parser.add_argument('stp', help='start offset of wav', type=float)
    parser.add_argument('length', help='append length(ms)', type=float)
    parser.add_argument('envelope', nargs='*', type=float,
                        help='envelope patern ' +
                        '\'p1 p2\' or \'p1 p2 p3 v1 v2 v3 v4 ove\'' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5\'')
    args = parser.parse_args()
    if (len(args.envelope) not in ARROW_ENVELOPE_VALUES):
        print("value error:envelope patern is not matching.")
    WavTool(args.output, args.input, args.stp, args.length, args.envelope)

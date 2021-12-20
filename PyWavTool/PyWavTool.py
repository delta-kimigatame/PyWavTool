
import os
import os.path
import wave
import argparse

import whd

ARROW_ENVELOPE_VALUES = [2, 8, 9, 10]


class WavTool:
    '''
    WavToolはUTAU標準のwavtoolをエミュレートします。
    wavを入力し、waveヘッダ(.wav.whd)とwaveデータ(.wav.dat)を出力します。
    すでにwhdとdatがある場合、datの末尾にデータを加え、whdを更新します。

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
            p1 p2
            p1 p2 p3 v1 v2 v3 v4 ove
            p1 p2 p3 v1 v2 v3 v4
            p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
        p1,p2,p3,p4,p5,ove : float
        v1,v2,v3,v4,v5 : int
    header : whd.Whd
        .whdファイルを扱います。
    '''
    __error: bool = False
    __output: str
    __input: str
    __stp: float
    __length: float
    __data: list
    __header: whd.Whd

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
                p1 p2 p3 v1 v2 v3 v4 ove
                p1 p2 p3 v1 v2 v3 v4
                p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
            p1,p2,p3,p4,p5,ove : float
            v1,v2,v3,v4,v5 : int
        '''
        self.__inputCheck(output,input,envelope)
        os.makedirs(os.path.split(output)[0], exist_ok=True)
        self.__header = whd.Whd(output + ".whd")

    def __inputCheck(self,output,input,envelope):
        '''
        入力値が正しいかチェックします。
        正常値の場合、self.__dataにwavの中身を代入します。
        異常値の場合、self.__errorをTrueにします。
        Parameters
        ----------
        ourput : str
            出力するwavのパス
        input : str
            入力するwavのパス
        envelope : list
            エンベロープのパターンは以下のいずれかです。
                p1 p2
                p1 p2 p3 v1 v2 v3 v4 ove
                p1 p2 p3 v1 v2 v3 v4
                p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
            p1,p2,p3,p4,p5,ove : float
            v1,v2,v3,v4,v5 : int
        '''
        if (len(envelope) not in ARROW_ENVELOPE_VALUES):
            # エンベロープがパターンにマッチしているか確認
            print("value error:envelope patern is not matching.")
            self.__error = True
        if (not os.path.isfile(input)):
            print("input file is not found:{}".format(input))
            self.__error = True
        try:
            with wave.open(input,"rb") as wr:
                self.__data=wr.readframes(wr.getnframes())
        except:
            print("file format error:{} is not wave.".format(input))
            self.__error = True



        


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
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5\'')
    args = parser.parse_args()
    if (len(args.envelope) not in ARROW_ENVELOPE_VALUES):
        print("value error:envelope patern is not matching.")
    WavTool(args.output, args.input, args.stp, args.length, args.envelope)

import os
import os.path

class Whd:
    '''
    whdはwaveファイルのヘッダのみのファイルです。
    wavtoolで生成したwhdとdatを結合するとwaveファイルになります。

    Attributes
    ----------
    __nchannels : int
        チャンネル数。モノラルなら1、ステレオなら2
    __samplewidth : int
        サンプルサイズ。8bitなら1、16bitなら2
    __framerate : int
        サンプリングレート。44100など
    __getnframes : int
        フレーム数。
    '''

    __nchannels: int
    __samplewidth: int
    __framerate: int
    __nframes: int

    @property
    def nchannels(self) -> int:
        return self.__nchannels
    
    @property
    def samplewidth(self) -> int:
        return self.__samplewidth
    
    @property
    def framerate(self) -> int:
        return self.__framerate
    
    @property
    def nframes(self) -> int:
        return self.__nframes

    def __init__(self, whdfile:str=""):
        '''
        Parameters
        ----------
        whdfile : str default ""
            whdファイルのパス。
            引数が与えられない場合やパスが無効な場合初期化されます。
        '''

        if (whdfile!="" and os.path.isfile(whdfile)):
            self.__read(whdfile)
        else:
            self.__nchannels = 1
            self.__samplewidth = 16
            self.__framerate = 44100
            self.__nframes = 0

    def __read(self, whdfile: str):
        '''
        whdファイルの読み込み。

        whdファイルを読み込んでself.__nchannels,self.__samplewidth,self.__framerate,self.__nframesに代入する。
        Parameters
        ----------
        whdfile : whdファイルのパス。
            事前にパスが通っているか検証要
        '''
        with open(whdfile, "rb") as fr:
            data:bytes = fr.read()
            self.__nchannels = int.from_bytes(data[22:24], 'little')
            self.__framerate = int.from_bytes(data[24:28], 'little')
            self.__samplewidth = int.from_bytes(data[34:36], 'little')
            self.__nframes = int.from_bytes(data[40:44], 'little') / self.__samplewidth *8

    def addframes(self, delta: int):
        '''
        __nframesをdelta分だけ増加させる。
        
        Parameters
        ----------
        delta : int
            増加させるフレーム数
        '''
        self.__nframes += delta

    def write(self, output: str):
        '''
        whdファイルをoutput.whdというファイル名保存する。
        Parameters
        ----------
        output : whdファイルのパス。
            不足するディレクトリは自動で作成する。
        '''
        if(os.path.split(output)[0] != ""):
            os.makedirs(os.path.split(output)[0], exist_ok=True)
        with open(output+".whd", "wb") as fw:
            fw.write(b"RIFF")
            fw.write(int((self.__nframes*self.__samplewidth/8 + 36)).to_bytes(4, 'little'))
            fw.write(b"WAVE")
            fw.write(b"fmt ")
            fw.write((16).to_bytes(4, 'little'))
            fw.write((1).to_bytes(2, 'little'))
            fw.write(self.__nchannels.to_bytes(2, 'little'))
            fw.write(self.__framerate.to_bytes(4, 'little'))
            fw.write(int((self.__framerate * self.__samplewidth/8 * self.__nchannels)).to_bytes(4, 'little'))
            fw.write(int((self.__samplewidth/8 * self.__nchannels)).to_bytes(2, 'little'))
            fw.write((self.__samplewidth).to_bytes(2, 'little'))
            fw.write(b"data")
            fw.write(int((self.__nframes*self.__samplewidth/8)).to_bytes(4, 'little'))
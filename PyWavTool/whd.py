import os
import os.path

class Whd:
    '''
    whdはwaveファイルのヘッダのみのファイルです。
    wavtoolで生成したwhdとdatを結合するとwaveファイルになります。

    Attributes
    ----------
    _nchannels : int
        チャンネル数。モノラルなら1、ステレオなら2
    _samplewidth : int
        サンプルサイズ。8bitなら1、16bitなら2
    _framerate : int
        サンプリングレート。44100など
    _getnframes : int
        フレーム数。
    '''

    _nchannels: int
    _samplewidth: int
    _framerate: int
    _nframes: int

    @property
    def nchannels(self) -> int:
        return self._nchannels
    
    @property
    def samplewidth(self) -> int:
        return self._samplewidth
    
    @property
    def framerate(self) -> int:
        return self._framerate
    
    @property
    def nframes(self) -> int:
        return self._nframes

    def __init__(self, whdfile:str=""):
        '''
        Parameters
        ----------
        whdfile : str default ""
            whdファイルのパス。
            引数が与えられない場合やパスが無効な場合初期化されます。
        '''

        if (whdfile!="" and os.path.isfile(whdfile)):
            self._read(whdfile)
        else:
            self._nchannels = 1
            self._samplewidth = 16
            self._framerate = 44100
            self._nframes = 0

    def _read(self, whdfile: str):
        '''
        whdファイルの読み込み。

        whdファイルを読み込んでself._nchannels,self._samplewidth,self._framerate,self._nframesに代入する。
        Parameters
        ----------
        whdfile : whdファイルのパス。
            事前にパスが通っているか検証要
        '''
        with open(whdfile, "rb") as fr:
            data:bytes = fr.read()
            self._nchannels = int.from_bytes(data[22:24], 'little')
            self._framerate = int.from_bytes(data[24:28], 'little')
            self._samplewidth = int.from_bytes(data[34:36], 'little')
            self._nframes = int.from_bytes(data[40:44], 'little') / self._samplewidth *8

    def addframes(self, delta: int):
        '''
        _nframesをdelta分だけ増加させる。
        
        Parameters
        ----------
        delta : int
            増加させるフレーム数
        '''
        self._nframes += delta

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
            fw.write(int((self._nframes*self._samplewidth/8 + 36)).to_bytes(4, 'little'))
            fw.write(b"WAVE")
            fw.write(b"fmt ")
            fw.write((16).to_bytes(4, 'little'))
            fw.write((1).to_bytes(2, 'little'))
            fw.write(self._nchannels.to_bytes(2, 'little'))
            fw.write(self._framerate.to_bytes(4, 'little'))
            fw.write(int((self._framerate * self._samplewidth/8 * self._nchannels)).to_bytes(4, 'little'))
            fw.write(int((self._samplewidth/8 * self._nchannels)).to_bytes(2, 'little'))
            fw.write((self._samplewidth).to_bytes(2, 'little'))
            fw.write(b"data")
            fw.write(int((self._nframes*self._samplewidth/8)).to_bytes(4, 'little'))
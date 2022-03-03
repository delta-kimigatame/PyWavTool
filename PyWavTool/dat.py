import os
import os.path

class Dat:
    '''
    wavファイルのヘッダ以外のデータ部分を扱います。
    
    Attributes
    ----------
    data :list of int
        wavファイルのデータ列
    '''

    _data: list

    @property
    def data(self) -> list:
        return self._data

    def __init__(self, input: str):
        '''
        Parameters
        ----------
        input :str
            datファイルのパス。存在しない場合作成されます。
        samplewidth :int
            wavのビット深度
        '''
        self._data = []
        self._input = input

    def read(self, samplewidth: int):
        '''
        | self._inputのデータを読み込んで、self._dataを更新します。
        | 既存の値は無視されます。
        
        Parameters
        ----------
        samplewidth :int
            wavのビット深度
        '''
        self._data = []
        with open(self._input ,"rb") as fr:
            tmp = fr.read()
        for i in range(int(len(tmp)/samplewidth*8)):
            self._data.append(int.from_bytes(tmp[i*int(samplewidth/8):(i+1)*int(samplewidth/8)], 'little', signed=True))


    def write(self, output: str, samplewidth: int):
        '''
        datファイルの保存

        Parameters
        ----------
        output :str
            datファイルのパス。存在する場合上書きされます。
        samplewidth :int
            wavのビット深度
        '''
        with open(output, "wb") as fw:
            for data in self._data:
                fw.write(data.to_bytes(int(samplewidth/8), 'little', signed=True))

    def addframe(self, data: list, ove: float, samplewidth: int, framerate: int) -> int:
        '''
        | self._datの末尾にdataを追加します。
        | ove(ms)分のデータは、self._dataとdataを加算します。

        Parameters
        ----------
        data :list of float
            書き込みするwavのデータ。1で正規化されている。
        ove :float
            既存のframeにかぶせる長さ(ms)
        samplewidth :int
            wavのビット深度
        framerate :int
            wavのサンプル周波数

        Returns
        -------
        nframes :int
            追加したフレーム数
        '''
        if os.path.exists(self._input):
            with open(self._input ,"rb") as fr:
                tmp = fr.read()
            for i in range(int(len(tmp)/samplewidth*8)):
                self._data.append(int.from_bytes(tmp[i*int(samplewidth/8):(i+1)*int(samplewidth/8)], 'little', signed=True))
        ove_frames :int = int(ove * framerate /1000)
        if ove_frames > len(self._data):
            ove_frames = len(self._data)

        ove_data=data[:ove_frames]

        for i in range(len(ove_data)):
            self._data[-i] += int((ove_data[-i] * ((2 ** (samplewidth)) /2)))
        for x in data[ove_frames:]:
            self._data.append(int(x * ((2 ** (samplewidth)) /2)))

        return len(data[ove_frames:])

    def addframeAndWrite(self, data: list, ove: float, samplewidth: int, framerate: int, output: str) -> int:
        '''
        | self._datの末尾にdataを追加します。
        | ove(ms)分のデータは、self._dataとdataを加算します。

        Parameters
        ----------
        data :list of float
            書き込みするwavのデータ。1で正規化されている。
        ove :float
            既存のframeにかぶせる長さ(ms)
        samplewidth :int
            wavのビット深度
        framerate :int
            wavのサンプル周波数
        output :str
            datファイルのパス。存在する場合上書きされます。

        Returns
        -------
        nframes :int
            追加したフレーム数
        '''
        ove_frames :int = int(ove * framerate /1000)
        sample_byte:int = int(samplewidth/8)
        max_amp:int = int((2**samplewidth)/2)
        data = list(map(lambda x: int(x * max_amp), data))
        if not os.path.exists(output):
            with open(output,"wb"):
                pass
        with open(output,"r+b") as fw:
            fw.seek(-ove_frames*2, 2)
            tmp=fw.read()
            for i in range(int(len(tmp)/sample_byte)):
                data[i] += int.from_bytes(tmp[i*sample_byte:(i+1)*sample_byte], 'little', signed=True)
            
            fw.seek(-ove_frames*2, 2)
            writer=b""
            for d in data:
                if d >= max_amp:
                    writer += (max_amp-1).to_bytes(sample_byte, 'little', signed=True)
                elif d <= 1-2**samplewidth/2:
                    writer += (2-max_amp).to_bytes(sample_byte, 'little', signed=True)
                else:
                    writer += d.to_bytes(sample_byte, 'little', signed=True)
            fw.write(writer)
                     
        return len(data[ove_frames:])
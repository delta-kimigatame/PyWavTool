import os
import os.path
import numpy as np

class Dat:
    '''
    wavファイルのヘッダ以外のデータ部分を扱います。
    
    Attributes
    ----------
    data :np.ndarray
        wavファイルのデータ列
    '''

    _data: np.ndarray

    @property
    def data(self) -> np.ndarray:
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
        self._data = np.array([])
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
        if samplewidth == 8:
            self._data = np.fromfile(self._input, dtype=np.int8)
        elif samplewidth == 16:
            self._data = np.fromfile(self._input, dtype=np.int16)
        elif samplewidth == 24:
            with open(self._input ,"rb") as fr:
                tmp = fr.read()
            for i in range(int(len(tmp)/samplewidth*8)):
                self._data.append(int.from_bytes(tmp[i*int(samplewidth/8):(i+1)*int(samplewidth/8)], 'little', signed=True))
            self._data = np.zeros(int(len(tmp)/3), dtype = "int32")
            for i in range(self._data.shape[0]):
                self._data[i] = int.from_bytes(tmp[i*3:(i+1)*3], "little", signed=True)
        elif samplewidth == 32:
            self._data = np.fromfile(self._input, dtype=np.int32)
        self._data = self._data.astype(np.float64)

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
        if samplewidth==8:
            data = self._data.astype("int8")
        elif samplewidth==16:
            data = self._data.astype("int16")
        elif samplewidth==24:
            data = self._data.astype("int32")
            for x in self._data:
                byte_data += x.to_bytes(3, "little", signed=True)
        elif samplewidth==32:
            data = self._data.astype("int32")
        with open(output,"wb") as fw:
            if samplewidth != 24:
                fw.write(data.tobytes())
            else:
                fw.write(byte_data)

    def addframe(self, data: np.ndarray, ove: float, samplewidth: int, framerate: int) -> int:
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
        ove_frames :int = int(ove * framerate /1000)
        if ove_frames > len(self._data):
            ove_frames = len(self._data)
            
        data *= ((2 ** (samplewidth)) /2)
        if ove_frames != 0:
            self._data[-ove_frames:] += data[:ove_frames]

        self._data = np.concatenate([self._data, data[ove_frames:]])
        #for x in data[ove_frames:]:
        #    self._data.append(int(x * ((2 ** (samplewidth)) /2)))

        return data[ove_frames:].shape[0]

    def addframeAndWrite(self, data: np.ndarray, ove: float, samplewidth: int, framerate: int, output: str) -> int:
        '''
        | self._datの末尾にdataを追加します。
        | ove(ms)分のデータは、self._dataとdataを加算します。

        Parameters
        ----------
        data :np.ndarray
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
        data = data * max_amp
        if not os.path.exists(output):
            with open(output,"wb"):
                pass
        with open(output,"r+b") as fw:
            fw.seek(-ove_frames*sample_byte, 2)
            tmp=fw.read()
            if samplewidth == 8:
                read_data: np.ndarray = np.frombuffer(tmp, dtype=np.int8)
            elif samplewidth == 16:
                read_data: np.ndarray = np.frombuffer(tmp, dtype=np.int16)
            elif samplewidth == 24:
                read_data: np.ndarray = np.zeros(int(len(tmp)/3), dtype = "int32")
                for i in range(self._data.shape[0]):
                    read_data[i] = int.from_bytes(tmp[i*3:(i+1)*3], "little", signed=True)
            elif samplewidth == 32:
                read_data: np.ndarraya = np.frombuffer(tmp, dtype=np.int32)

            
            if ove_frames != 0:
                data[:ove_frames] += read_data

            #data = np.concatenate([read_data, data[ove_frames:]])
                
            fw.seek(-ove_frames*sample_byte, 2)
            if samplewidth==8:
                data = data.astype("int8")
            elif samplewidth==16:
                data = data.astype("int16")
            elif samplewidth==24:
                data = data.astype("int32")
                for x in data:
                    byte_data += x.to_bytes(3, "little", signed=True)
            elif samplewidth==32:
                data = data.astype("int32")
            if samplewidth != 24:
                fw.write(data.tobytes())
            else:
                fw.write(byte_data)
                     
        return data[ove_frames:].shape[0]
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

    def __init__(self, input: str, samplewidth: int):
        '''
        Parameters
        ----------
        input :str
            datファイルのパス。存在しない場合作成されます。
        samplewidth :int
            wavのビット深度
        '''
        self._data = []
        samplewidth = int(samplewidth/8)
        if not os.path.exists(input):
            return
        with open(input ,"rb") as fr:
            tmp = fr.read()
        for i in range(int(len(tmp)/samplewidth)):
            self._data.append(int.from_bytes(tmp[i*samplewidth:(i+1)*samplewidth], 'little', signed=True))

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
                print(data)
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
        ove_frames :int = int(ove * framerate /1000)
        if ove_frames > len(self._data):
            ove_frames = len(self._data)

        ove_data=data[:ove_frames]

        for i in range(len(ove_data)):
            self._data[-i] += int((ove_data[-i] * ((2 ** (samplewidth)) /2)))
        for x in data[ove_frames:]:
            self._data.append(int(x * ((2 ** (samplewidth)) /2)))

        return len(data[ove_frames:])

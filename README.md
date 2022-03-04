# PyWavTool

### これは何?
* 飴屋／菖蒲氏によって公開されている、Windows向けに作成された歌声合成ソフトウェア「UTAU」に同梱されている、wavファイル結合用ソフトwavtool.exeの互換プロジェクトです。

    UTAU公式サイト(http://utau2008.web.fc2.com/)

* wavファイルを読み込んで、.whdと.datを生成・更新します。
* このプロジェクト単体ではあまり意味がありません。

***

### 免責事項
* 本ソフトウェアを使用して生じたいかなる不具合についても、作者は責任を負いません。
* 作者は、本ソフトウェアの不具合を修正する責任を負いません。


***

### PyWavToolExe.exeの使い方
1. releaseからPyWavTool-[公開日].zipをダウンロードしてください。(https://github.com/delta-kimigatame/PyWavTool/releases)
2. 任意の場所でzipを解凍してください。
3. UTAUのプロジェクトのプロパティを開き、ツール1(append)にPyWavToolExe.exeを設定してください。

***

### モジュールの使い方

#### インストール
``` pip install PyWavTool```

#### 使い方
```#python
import PyWavTool

#class init
wavtool = PyWavTool.WavTool("output_path.wav")

#input
wavtool.inputCheck("input_path.wav")
wavtool.setEnvelope([0, 5, 30, 100, 100, 100, 100])

#update output_path.wav.dat
wavtool.applyData(stp, ms_length)

#update output_path.wav.whd
wavtool.write()

#make wav
with open("output_path.wav", "wb") as fw:
    with open("output_path.wav.whd", "rb") as fr:
        fw.write(fr.read())
    with open("output_path.wav.dat", "rb") as fr:
        fw.write(fr.read())
```

***

### 技術仕様
APIについては(https://delta-kimigatame.github.io/PyWavTool/)

***

### リンク
* twitter(https://twitter.com/delta_kuro)
* github(https://github.com/delta-kimigatame/MakeOtoTemp)
def str2float(length :str) -> float:
    '''
    UTAUのLength文字列をfloatに変換します。
    
    Parameters
    ----------
    length :str
        length文字列

    Returns
    -------
    length :float


    Notes
    -----
    | lengthは以下のいずれかの形で与えられます。
    | tick@tempo
    | tick@tempo+delta
    | tick@tempo-delta
    
    | 戻り値の計算は以下の通りです。
    | 1拍あたりのms = 60*1000 / tempo
    | 1tickあたりのms = 1拍あたりのms / 480
    | length = 1tickあたりのms * tick +(-) delta
    '''
    temp: str = length.split("@")
    tempo :float
    delta :float =0
    tick: int = int(temp[0])
    if "+" in temp[1]:
        tempo = float(temp[1].split("+")[0])
        delta = float(temp[1].split("+")[1])
    elif "-" in temp[1]:
        tempo = float(temp[1].split("-")[0])
        delta = float(temp[1].split("-")[1])
    else:
        tempo=float(temp[1])

    return 60000 / tempo / 480 * tick + delta


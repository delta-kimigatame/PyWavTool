
import os.path
import wave
import argparse

ARROW_ENVELOPE_VALUES = [2, 8, 9, 10]


class WavTool:
    '''
    WavTool is emulate UTAU's wavtool.
    input wav to output wavheader(output.whd) and wavbody(output.wbd)

    Attributes
    ----------
    ourput : str
        output wav path
    input : str
        input wav path
    stp : float
        start offset of wav
    length : float
        append ms
    envelope : list
        envelope patern is
            p1 p2
            p1 p2 p3 v1 v2 v3 v4 ove
            p1 p2 p3 v1 v2 v3 v4
            p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
        p1,p2,p3,p4,p5,ove : float
        v1,v2,v3,v4,v5 : int
    '''
    __error: bool = False
    __output: str
    __input: str
    __stp: float
    __length: float

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
            output wav path
        input : str
            input wav path
        stp : float
            start offset of wav
        length : float
            append ms
        envelope : list
            envelope patern is
                p1 p2
                p1 p2 p3 v1 v2 v3 v4 ove
                p1 p2 p3 v1 v2 v3 v4
                p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5
            p1,p2,p3,p4,p5,ove : float
            v1,v2,v3,v4,v5 : int
        '''
        if (len(args.envelope) not in ARROW_ENVELOPE_VALUES):
            # is amount of envelope values matching patern?
            print("value error:envelope patern is not matching.")
            self.__error = True
        if (not os.path.isfile(input)):
            print("input file is not found:{}".format(input))
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

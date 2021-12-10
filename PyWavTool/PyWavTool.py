
import argparse

ARROW_ENVELOPE_VALUES = [2, 8, 9, 10]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This module emulate UTAU\'s wavtool')
    parser.add_argument('output', help='output wav path', type=str)
    parser.add_argument('input', help='input wav path', type=str)
    parser.add_argument('stp', help='start offset of wav', type=float)
    parser.add_argument('envelope', nargs='*', type=float,
                        help='envelope patern ' +
                        '\'p1 p2\' or \'p1 p2 p3 v1 v2 v3 v4 ove\'' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove\'' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4' +
                        ' or \'p1 p2 p3 v1 v2 v3 v4 ove p4 p5 v5\'')
    args = parser.parse_args()
    if (len(args.envelope) not in ARROW_ENVELOPE_VALUES):
        raise ValueError("envelope patern is not matching.")

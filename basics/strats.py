import pandas as pd
from NFA_patternrecognition import NFA
import itertools

nfa = NFA()
# Green, Red, "Upper Boll crossing", "Lower Boll crossing", "Moving average crossing above", "Moving average crossing below"
EVENTS = ["G", "R", "UB+", "UB-", "LB+", "LB-", "MA+", "MA-"]
POS_EVENTS = ["G", "MA+", "UB+", "LB+"]
NEG_EVENTS = ["R", "MA-", "UB-", "LB-"]
OUTS = ['Buy', 'Sell']

patterns = [
    [["G", "G", "MA+"], "Buy"],  # Moving Average crossing up after two green candles
    [["G", "G", "G", "G"], "Buy"],  # 4 consecutive green candles
    [["G", "G", "UB+", "UB+"], "Buy"],  # 2 green candles followed by 2 upper band crosses
    [["G", "G", "UB+", "G"], "Buy"],  # Green candles followed by an upper band cross and more green
    [["G", "R", "R", "R", "G"], "Buy"],  # A mixed trend with a green candle at the end
    [["R", "R", "MA-"], "Sell"],  # Moving Average crossing down after two red candles
    [["R", "R", "LB-", "LB-"], "Sell"],  # 2 red candles followed by 2 lower band crosses
    [["R", "R", "LB-", "R"], "Sell"],  # Red candles followed by a lower band cross and more red
    [["R", "R", "R", "R"], "Sell"],  # 4 consecutive red candles
    [["G", "G", "G", "LB+"], "Buy"],  # 3 green candles followed by a lower band cross
    [["R", "R", "R", "UB-"], "Sell"],  # 3 red candles followed by an upper band cross
    [["G", "G", "G", "UB+"], "Buy"],  # 3 green candles followed by an upper band cross
    [["R", "R", "R", "LB-"], "Sell"],  # 3 red candles followed by a lower band cross
    [["G", "G", "G", "MA+"], "Buy"],  # 3 green candles followed by a moving average crossing up
    [["R", "R", "R", "MA-"], "Sell"],  # 3 red candles followed by a moving average crossing down
]


def create_events(df: pd.DataFrame, encoded:bool) -> pd.DataFrame:
    global EVENTS
    global patterns
    def determine_event(row):
        # Start with basic bullish/bearish event
        if row['close'] > row['open']:
            event = 'G'
        else:
            event = 'R'

        # Cross middle band
        if (row['open'] < row['middle_band']) and (row['close'] > row['middle_band']):
            event = 'MA+'
        elif (row['open'] > row['middle_band']) and (row['close'] < row['middle_band']):
            event = 'MA-'

        # Cross upper band
        if (row['open'] < row['upper_band']) and (row['close'] > row['upper_band']):
            event = 'UB+'
        elif (row['open'] > row['upper_band']) and (row['close'] < row['upper_band']):
            event = 'UB-'

        # Cross lower band
        if (row['open'] < row['lower_band']) and (row['close'] > row['lower_band']):
            event = 'LB+'
        elif (row['open'] > row['lower_band']) and (row['close'] < row['lower_band']):
            event = 'LB-'

        return event 
    df['event'] = df.apply(determine_event, axis=1)

    print(*patterns, sep='\n')
    if encoded:
        for p,o in patterns:
            p = list(map(lambda x: EVENTS.index(x), p))
            o = OUTS.index(o)
            nfa.add_pattern(p,o)
        df['event'] = df['event'].apply(lambda x: EVENTS.index(x))
    else:
        for p,o in patterns:
            nfa.add_pattern(p,o)
    return df


def check_patterns(df: pd.DataFrame):
    df = create_events(df, encoded=True)
    print(df)
    global nfa

    def process_matches(x):
        out = nfa.check(x)
        if (out is not None) and (len(out) > 0):
            print(out)
            return out[0]
        else:
            return -1
    df['signal'] = df['event'].rolling(nfa.max_len).apply(process_matches, raw=True)
    print(list(df['signal']))
    return df

    
def bollbands(df: pd.DataFrame, period: int):
    df['middle_band'] = df['close'].rolling(window=period).mean()
    df['std_dev'] = df['close'].rolling(window=period).std()
    df['upper_band'] = df['middle_band'] + (2 * df['std_dev'])
    df['lower_band'] = df['middle_band'] - (2 * df['std_dev'])
    df.fillna(method='bfill', inplace=True)
    return df
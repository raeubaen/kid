import pandas as pd
import soundfile as sf
import sys
import numpy as np

# assume we have columns 'time' and 'value'
df = pd.read_csv('~/Documenti/Fisica/magistrale/2 semestre/lab2/wave_forms/04-05-2021, 16.22.15/signal.dat', sep=" ")

def custom_round(x, base=5):
    return int(base * round(float(x)/base))

df.time = (df.time).apply(lambda x: custom_round(x, base=20))

df = df.drop_duplicates(subset=["time"])

df.time = pd.to_datetime(df.time, unit='us')

df = df.set_index(df.time).asfreq("20U").bfill()

df.time = df.index.astype(np.int64) / int(1e3)

df.to_csv("garbage.csv", sep=" ")


# compute sample rate, assuming times are in seconds
times = df['time'].values / 1e6
n_measurements = len(times)
timespan_seconds = times[-1] - times[0]
sample_rate_hz = int(n_measurements / timespan_seconds)

# write data
data = (df['v'].values - df['v'].mean())/2000
sf.write('recording.wav', data.astype("float32"), sample_rate_hz)

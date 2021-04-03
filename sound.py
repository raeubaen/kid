import pandas as pd
import soundfile as sf

# assume we have columns 'time' and 'value'
df = pd.read_csv('garbage.csv', sep=" ")

# compute sample rate, assuming times are in seconds
times = df['time'].values / 1e6
n_measurements = len(times)
timespan_seconds = times[-1] - times[0]
sample_rate_hz = int(n_measurements / timespan_seconds)

# write data
data = (df['I'].values - df['I'].mean())/2000
sf.write('recording.wav', data.astype("float32"), sample_rate_hz)

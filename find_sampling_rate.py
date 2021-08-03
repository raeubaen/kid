import pandas as pd
import matplotlib.pyplot as plt
import sys

df = pd.read_csv(sys.stdin, sep= " " )
df.columns = ["i", "q", "t"]
df = df.sort_values(["t"])

df = df[df.t.diff().argmax():]

rate = (df.t.max()-df.t.min())/(df.t.argmax()-df.t.argmin())

print(rate)

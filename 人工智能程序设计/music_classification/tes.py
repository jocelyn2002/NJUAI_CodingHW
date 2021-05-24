import librosa
import numpy as np
import pandas as pd
import librosa.display
from sklearn.decomposition import PCA
import time
import matplotlib.pyplot as plt
import sys


x, sr = librosa.load('Jason Piano - 最想環遊全世界 钢琴曲（Cover：梁靜茹）流行钢琴 Jason Piano Cover.mp3', sr=None)
a = librosa.feature.zero_crossing_rate(x, sr)

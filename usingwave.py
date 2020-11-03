import numpy as np
import matplotlib.pyplot as plt 
import wave # wavファイルを扱うライブラリのインポート
from scipy.signal import fftconvolve # 畳み込みの関数をインポート

def readwav(filename):
    '''
    Parameter
    ---------
    filename: strings
        filaname of wave file
    '''
    wr = wave.open(filename, 'r')
    params = wr.getparams()
    nchannels = params[0]
    sampwidth = params[1]
    rate = params[2]
    nframes =  params[3]
    frames = wr.readframes(nframes)
    wr.close()

    if sampwidth == 1:
        data = np.frombuffer(frames, dtype=np.uint8)
        data = (data - 128) / 128
    elif sampwidth == 2:
        data = np.frombuffer(frames, dtype=np.int16) / 32768
    elif sampwidth == 3:
        a8 = np.frombuffer(frames, dtype=np.uint8)
        tmp = np.zeros((nframes * nchannels, 4), dtype=np.uint8)
        tmp[:, 1:] = a8.reshape(-1, 3)
        data = tmp.view(np.int32)[:, 0] / 2147483648
    elif sampwidth == 4:
        data = np.frombuffer(frames, dtype=np.int32) / 2147483648
    
    data = np.reshape(data, (-1, nchannels))
    return rate, data

def writewav(filename, data, ws=3, fs=48000, e=-1):
    '''
    Parameters
    ----------
    filename: strings
        frequency of sine-wave
    data: numpy.ndarray
        number of samples of sine-wave
    ws: int
        byte width of samples.
        1: 8 bit, 2: 16 bit, 3: 24 bit, 4: 32 bit
    fs: int
        sampling rate
    '''
    nchannels = data.shape[1]
    sampwidth = ws
    data = (data * (2 ** (8 * sampwidth - 1) + e)).reshape(data.size, 1)
    
    if sampwidth == 1:
        data = data + 128
        frames = data.astype(np.uint8).tostring()
    elif sampwidth == 2:
        frames = data.astype(np.int16).tostring()
    elif sampwidth == 3:
        a32 = np.asarray(data, dtype = np.int32)
        a8 = (a32.reshape(a32.shape + (1,)) >> np.array([0, 8, 16])) & 255
        frames = a8.astype(np.uint8).tostring()
    elif sampwidth == 4:
        frames = data.astype(np.int32).tostring()
    
    w = wave.open(filename, 'wb')
    w.setparams((nchannels, sampwidth, fs, 0, 'NONE', 'not compressed'))
    w.writeframes(frames)
    w.close()
    return
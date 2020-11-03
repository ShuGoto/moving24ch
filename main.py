import numpy as np
import usingwave
from scipy.signal import fftconvolve
import matplotlib.pyplot as plt


# 開始点，終了点，速度，回転方向を入力し，１つの方向の畳み込み時間を計算
def convtime(start, end, moving_speed, rotation):
    if rotation == 1 and end > start:
        convolution_time = moving_speed/(end - start)
    elif rotation == 1 and start > end:
        convolution_time = moving_speed/(360 - start + end)
    elif rotation == 0 and start > end:
        convolution_time = moving_speed/(start - end)
    elif rotation == 0 and end > start:
        convolution_time = moving_speed/(start + 360 - end)
    return convolution_time

# 開始点，終了点，回転方向を入力し，畳み込む角度の数を計算
def point(start, end, rotation):
    if rotation == 1 and end > start:
        point = end - start
    elif rotation == 1 and start > end:
        point = 360 - start + end
    elif rotation == 0 and start > end:
        point = start - end
    elif rotation == 0 and end > start:
        point = start + 360 - end
    return point

# 水平方向の数値から，ファイル抽出のため0を詰めてstrに
def azi(azinum):
    if azinum < 0:
        azinum = 360 + azinum
    elif azinum >= 360:
        azinum = azinum - 360
    if azinum - 10 < 0:
        azi = "00" + str(azinum)
    elif azinum - 100 < 0:
        azi = "0" + str(azinum)
    else:
        azi = str(azinum)
    return azi


if __name__ == '__main__':
    # 各種入力
    # file = input("using file:")
    # fs, soundfile = usingwave.readwav(file)
    fs, sounddata = usingwave.readwav("/Users/shugoto/pink15.wav") #仮置き
    start = int (input("enter start point (0 ~ 360):"))
    end = int(input("enter end point (0 ~ 360):"))
    moving_speed = float(input("enter moving speed (radian):"))
    rotation = int(input("enter rotation direction(clock:1 reverse:0):"))

    conv_time = convtime(start, end, moving_speed, rotation)
    conv_point = point(start, end, rotation)

    # 生成する配列をあらかじめ作成（不要かも）
    convolve_sound = np.zeros((24, (conv_point + 1)*int(conv_time*48000) + 4095))

    # ir，390から畳み込みを検証
    for i in range(conv_point):
        # 回転方向ごとにIRを抽出
        if rotation == 1:
            azimuth = azi(start + i)
            ir_filename = '/Users/shugoto/Desktop/IR/補完IR/ir_4096taps_elevetion090_azimuth{0}.npy'. format(azimuth)
            print(ir_filename)
            ir = np.load(ir_filename)
            conv_ir = ir[:, 0:4096]

        elif rotation == 0:
            azimuth = azi(start - i)
            ir_filename = '/Users/shugoto/Desktop/IR/補完IR/ir_4096taps_elevetion090_azimuth{0}.npy'. format(azimuth)
            print(ir_filename)
            ir = np.load(ir_filename)
            conv_ir = ir[:, 0:4096]

        # 音源切り出しの位置，conv_time * 48000が１つの角度に対する音源の畳み込み時間となる
        point = int(i * conv_time * 48000)

        # 音源切り出し，
        sound = sounddata[point: point + int(conv_time*48000)]

        # 切り出した音源とIRを畳み込み
        convolve = fftconvolve(sound[:, 0].T, conv_ir[0, :])

        for j in range(23):
            con = fftconvolve(sound[:, 0].T, conv_ir[j + 1, :])
            convolve = np.block([[convolve], [con]])

        # 前後に0を詰める
        append_zero_before = np.zeros((24, i*int(conv_time*48000)))
        append_zero_after = np.zeros((24, (conv_point - i)*int(conv_time*48000)))
        convolve_zero = np.append(append_zero_before.T, convolve.T, axis=0)
        convolve_zero = np.append(convolve_zero, append_zero_after.T, axis=0)
        convolve_zero /= 40
        convolve_sound += convolve_zero.T

    if rotation == 1:
        clock = "clock"
    elif rotation == 0:
        clock = "counterclock"
    moving_speed *= 1000
    print("moving{0}-{1}with{2}ms-{3}.wav will be the filename".format(start, end, int(moving_speed), clock))
    confirm = input("ok(1) or change(0) : ")
    if confirm == "1":
        filename = "moving{0}-{1}with{2}-{3}.wav will be the filename".format(start, end, moving_speed, clock)
    elif confirm == "0":
        filename = input("filename:")
    usingwave.writewav(filename, convolve_sound.T)























# 引入库
import wave
import pyaudio
chunk = 1024
f = wave.open("蜂鸟+-+吴青峰.wav", "rb")
p = pyaudio.PyAudio()
rate = f.getframerate()
stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                channels=f.getnchannels(), rate=rate, output=True)
RATE / CHUNK * RECORD_SECONDS
# 读取数据
data = f.readframes(chunk)

# 播放
while data != "":
    stream.write(data)
    data = f.readframes(chunk)

# 停止数据流
stream.stop_stream()
stream.close()
# 关闭 PyAudio
p.terminate()

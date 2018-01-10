
import matplotlib as mpl

mpl.use('TkAgg')
# read audio samples
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import numpy as np
import wave

SAMPLES_PER_SCND = 0

def read_aeneas_mapping(filename="rules.json"):
    
    import json

    with open(filename) as json_data:
        d = json.load(json_data)

        return d['fragments']

def chunkit(zipped_channel, time_min, time_max):
    
    chunk = []
    amplitude = []
    
    for time, data in zipped_channel:
        
        if time < time_min:
            continue
        if time > time_max:
            break

        chunk.append((time, data))
        amplitude.append(data)
    if len(amplitude) == 0:
        track = [tupl[1] for tupl in zipped_channel]
        print(len(track))
        print(time_min)
        raise Exception("mean 0")

    #print(len(amplitude), time_min, time_max)

    return chunk, np.mean(np.abs(amplitude))

def get_significant_channel(file="rules_foreground.wav"):
    
    global SAMPLES_PER_SCND

    with wave.open(file,'r') as wav_file:
        #Extract Raw Audio from Wav File
        signal = wav_file.readframes(-1)
        signal = np.fromstring(signal, 'Int16')

        #Split the data into channels 
        channels = [[] for channel in range(wav_file.getnchannels())]
        for index, datum in enumerate(signal):
            channels[index%len(channels)].append(datum)

        #Get time from indices
        
        fs = wav_file.getframerate()
        Time = np.linspace(0, len(signal)/len(channels)/fs, num=len(signal)/len(channels))

        SAMPLES_PER_SCND = fs

        def channel_amplitude_avg(channel):
            return np.mean(np.abs(channel))


        avg_c1 = channel_amplitude_avg(channels[0])
        avg_c2 = channel_amplitude_avg(channels[1])
        avg = 0.0

        channel = None

        if avg_c1 > avg_c2:
            channel = channels[0]
            avg = avg_c1
        else:
            channel = channels[1]
            avg = avg_c2

        zipped_channel = zip(Time, channel)
        return zipped_channel, avg

def match_chunk_in_track(chunk,track,start=0):
    i = start
    while True:
        success = True
        for index,dot in enumerate(chunk):
            if (abs(dot - track[i+index]) > 0.01):
                success = False
                break
            else:
                print("O?O")
        if success:
            return i
        i += 1
        if i == len(track):
            raise Exception("WTF!!")


def main():
    zipped_channel, avg = get_significant_channel()
    aeneas_fragments = read_aeneas_mapping()

    track = [tupl[1] for tupl in zipped_channel]
    print('***', len(track))
    track = [tupl[1] for tupl in zipped_channel]
    print('***', len(track))

    min_mean = avg

    chunks = []
    final_chunks = []
    soundless_chunks = []

    for fragment in aeneas_fragments:
        print("track")
        track = [tupl[1] for tupl in zipped_channel]
        print(len(track))

        begin = float(fragment['begin'])
        end = float(fragment['end'])
        if begin == end:
            continue
        id_ = fragment['id']

        print('==>', id_)

        print("track", zipped_channel)
        track = [tupl[1] for tupl in list(zipped_channel)]
        print('+++', len(track))

        chunk, mean = chunkit(zipped_channel, begin, end)
        chunks.append((chunk, mean))
        min_mean = min(mean, min_mean)
    track = [tupl[1] for tupl in zipped_channel]
    print(len(track))

    for chunk, mean in chunks:

        avg_distance = abs(avg - mean)
        min_distance = abs(min_mean - mean)

        if avg_distance < min_distance:
            soundless_chunk = [d for _, d in chunk]
            final_chunks += soundless_chunk
            soundless_chunks.append(soundless_chunk)
    track = [tupl[1] for tupl in zipped_channel]
    print(len(track))

    Time = np.linspace(0, len(final_chunks)/SAMPLES_PER_SCND, num=len(final_chunks))
    final_chunks = zip(Time,final_chunks)

    last_chunk_pos = 0
    print("bfore")
    track = [tupl[1] for tupl in zipped_channel]
    print(len(track))

    for fragment in read_aeneas_mapping('rules_test.json'):
        begin = float(fragment['begin'])
        end = float(fragment['end'])

        chunk,_ = chunkit(final_chunks, begin, end)

        print("yay")
        track = [tupl[1] for tupl in zipped_channel]
        print(track)
        chunk = [tupl[1] for tupl in chunk]
        chunk_pos = match_chunk_in_track(chunk,track,start=last_chunk_pos)
        last_chunk_pos = chunk_pos

        fragment['begin'] = float(chunk_pos)/SAMPLES_PER_SCND 
        fragment['end']   = float(chunk_pos + len(chunk))/SAMPLES_PER_SCND
        #print(fragment)

    #print() 
    write('rules_test.wav', SAMPLES_PER_SCND, np.array(final_chunks))
    #write('test.wav', len(final_chunks), np.array(final_chunks))
    

main()


    


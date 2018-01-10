from aeneas.executetask import ExecuteTask
from aeneas.task import Task

from scipy.io.wavfile import write
import numpy as np
import wave
import json

def channel_amplitude_avg(channel):
    return np.mean(np.abs(channel))

def get_significant_channel(foreground_file_name):

    with wave.open(foreground_file_name,'r') as wav_file:
        # Extract Raw Audio from Wav File
        signal = wav_file.readframes(-1)
        signal = np.fromstring(signal, 'Int16')

        # Split the data into channels 
        channels = [[] for channel in range(wav_file.getnchannels())]
        for index, datum in enumerate(signal):
            channels[index % len(channels)].append(datum)

        #Get time from indices
        fs = wav_file.getframerate()
        time_array = np.linspace(0, len(signal) / len(channels) / fs, num=len(signal) / len(channels))

        # Select most significant channel
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

        return time_array, channel, avg, fs

def run_aeneas_task(audio_filepath, lyrics_filepath, output_filepath):
    config_string = "task_language=eng|os_task_file_format=json|is_text_type=plain"

    task = Task(config_string=config_string)

    task.audio_file_path_absolute = audio_filepath
    task.text_file_path_absolute = lyrics_filepath
    task.sync_map_file_path_absolute = output_filepath

    # process Task
    ExecuteTask(task).execute()

    # output sync map to file
    task.output_sync_map_file()

def read_aeneas_mapping(filename):

    with open(filename) as json_data:
        d = json.load(json_data)
        return d['fragments']

def chunkit(time_array, channel, time_min, time_max):
    
    time_chunk, data_chunk = [], []
    
    for idx, time in enumerate(time_array):
        
        data = channel[idx]
        
        if time < time_min:
            continue
        if time > time_max:
            break

        time_chunk.append(time)
        data_chunk.append(data)

    return time_chunk, data_chunk, np.mean(np.abs(data_chunk))

def write_soundless_wav(time_array, channel, avg, aeneas_original_filename, fs):
    
    aeneas_fragments = read_aeneas_mapping(aeneas_original_filename)

    min_mean = avg

    chunks = []
    final_data_chunks = []

    for fragment in aeneas_fragments:

        begin = float(fragment['begin'])
        end = float(fragment['end'])

        if begin == end:
            continue

        _, chunk, mean = chunkit(time_array, channel, begin, end)
        chunks.append((chunk, mean))
        min_mean = min(mean, min_mean)

    for chunk, mean in chunks:

        avg_distance = abs(avg - mean)
        min_distance = abs(min_mean - mean)

        if avg_distance < min_distance:
            final_data_chunks += chunk

    final_time_chunks = np.linspace(0, len(final_data_chunks) / fs, num=len(final_data_chunks))

    filename = aeneas_original_filename.split('.')[0] + '_soundless.wav'
    write(filename, fs, np.array(final_data_chunks))

    return final_time_chunks, final_data_chunks, filename

def process_soundless_file(tchunk, dchunk, time_array, channel, aeneas_soundless_filename):
    
    aeneas_fragments = read_aeneas_mapping(aeneas_soundless_filename)

    for fragment in aeneas_fragments:
    
        begin = float(fragment['begin'])
        end = float(fragment['end'])

        if begin == end:
            continue

        _, chunk, _ = chunkit(tchunk, dchunk, begin, end)
    
def _test():
    
    song_id = 'rules'
    
    lyrics_file = f'{song_id}.txt'
    original_wav = f'{song_id}.wav'
    aeneas_filename = f'{song_id}.json'
    foreground_file_name = f'{song_id}_foreground.wav'

    # Run aeneas on original_wav with lyrics_file
    run_aeneas_task(original_wav, lyrics_file, aeneas_filename)

    # TODO: run REPET algorithm on original_wav to generate foreground_file_name

    time_array, channel, avg, fs = get_significant_channel(foreground_file_name)
    tchunk, dchunk, fn = write_soundless_wav(time_array, channel, avg, aeneas_filename, fs)

    # Run aeneas on fn with lyrics_file
    aeneas_soundless_filename = f'{song_id}_soundless.json'
    run_aeneas_task(fn, lyrics_file, aeneas_soundless_filename)

    #process_soundless_file(tchunk, dchunk, time_array, channel, aeneas_soundless_filename)
    
_test()
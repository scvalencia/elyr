% Read the audio file, here, corresponding to a song
[audio_signal, sample_rate] = audioread('rules.wav');

% Estimate the background using repet-SIM, and derive the 
% corresponding foreground (the parameters of the algorithm can be 
% redefined if necessary, in the properties of the class)
background_signal = repet.adaptive(audio_signal, sample_rate);
foreground_signal = audio_signal-background_signal;

% Write the background and foreground files, here corresponding to 
% the accompaniment and vocals, respectively
audiowrite('rules_accompaniment.wav', background_signal, sample_rate)
audiowrite('rules_foreground.wav', foreground_signal, sample_rate)
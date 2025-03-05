
import numpy as np
import wave
import subprocess
import matplotlib.pyplot as plt
import speech_recognition as sr
# from .audio import AudioData, get_flac_converter
from speech_recognition import AudioData


class SpeechToText:
    def __init__(self):
        self.audio_frames = []
        self.word_frame = 0
        self.stop_log = False

        self.words = []
        self.silence_time = 1  # can be somewhere between 0.5 and 3
        self.silence_threshold = 1000
        self.silence_threshold2 = 10  # can be somewhere between 100 and 400
        self.max_length_audio = 10

        self.sample_rate = 16000

        self.mode_continues = False
        self.new_words = False
        self.processing = False
        self.silence_counter = 0
        self.to_proses_frames = []

        self.do_speech = True
        self.logging = False
        self.set_log_level = "debug"

        self.save_to_wav = False

        self.language_setting = "en-US"

        self.notify_once = True

        # subprocess.run("rm -rf output/*", shell=True)

        # self.loop()

    def logger(self, type, string):
        log_levels = ["minimal", "error", "info", "debug"]

        if self.set_log_level not in log_levels:
            self.set_log_level = "debug"
            self.logger("error", "log level not supported setting to debug")

        requested_log_level = log_levels.index(self.set_log_level)

        if type == "minimal":
            state = 0
        if type == "error":
            state = 1
        if type == "info":
            state = 2
        if type == "debug":
            state = 3

        if self.logging:
            if requested_log_level >= state:
                print(f"#{type}# {string}")

    def loop(self):
        if self.processing:
            self.logger("debug", "start processor")
            self.proses_audio(self.to_proses_frames.pop())

    def listen(self, data):  # todo is deze functie nog nodig
        frame_single = data["data"]["body.head"]
        if frame_single is None:
            pass
        else:
            audio_np = np.frombuffer(frame_single, dtype=np.int16)
            # print(audio_np)
            self.logger("debug", f"audio frame {audio_np[0]}")
            self.audio_frames.append(audio_np)

    def listen_split(self, data):
        self.mode_continues = False
        frame_single = data["data"]["body.head"]
        if frame_single is None:
            pass
        else:
            audio_np = np.frombuffer(frame_single, dtype=np.int16)
            # print(audio_np)
            try:
                self.logger("debug", f"audio frame {audio_np[0]}")
                self.audio_frames.append(audio_np)
                # if len(self.audio_frames) > 500:
                # self.audio_splitter()

            except:
                self.logger("error", "can not append audio frame")

    def listen_continues(self, data):
        if self.do_speech:
            if self.notify_once:
                self.logger("minimal", "speech recognition is turned on")
            self.notify_once = False

            self.mode_continues = True
            frame_single = data["data"]["body.head"]
            # print(len(self.audio_frames))
            if frame_single is None:
                pass
            else:
                audio_np = np.frombuffer(frame_single, dtype=np.int16)
                # print(audio_np)
                try:
                    self.logger("debug", f"noise level {audio_np[0]} total data {len(self.audio_frames)} packets {round(len(self.audio_frames)*0.1,2)} seconds")
                    self.audio_frames.append(audio_np)

                except:
                    self.logger("error", "can not append to audio frames")

                for packet in audio_np:
                    # print(f"packet: {packet}")
                    if abs(packet) < self.silence_threshold2:
                        self.silence_counter += 1
                    else:
                        # print("reset silence")
                        # pass
                        self.silence_counter -= 1
                        if self.silence_counter < 0:
                            self.silence_counter = 0

                if (len(self.audio_frames)*0.1) > 10:
                    self.logger("info", f"max audio length reached {round(len(self.audio_frames)*0.1,2)} seconds")
                    self.to_proses_frames.append(self.audio_frames)
                    self.processing = True
                    self.audio_frames = []
                    self.silence_counter = 0

                min_silence_samples = int(self.sample_rate * self.silence_time)
                if self.silence_counter > min_silence_samples and self.processing == False:
                    self.silence_counter = 0
                    self.logger("info", "got silence initiating processing")

                    self.to_proses_frames.append(self.audio_frames)
                    self.processing = True
                    # self.proses_audio(self.to_proses_frames)
                    self.audio_frames = []
                    self.silence_counter = 0
        else:
            self.audio_frames = []
            if not self.notify_once:
                self.logger("minimal", "not listening speech recognition is turned off")
                self.notify_once = True
            pass

    def split_audio(self, audio_data):
        silence_threshold = 100
        # min_silence_duration = self.silence_time
        sample_rate = 16000
        min_silence_samples = int(sample_rate * self.silence_time)

        silent_regions = np.where(np.abs(audio_data) < silence_threshold)[0]

        if len(silent_regions) == 0:
            return [audio_data]

        # Find silence segment start and end indices
        split_points = []
        prev_silent_sample = silent_regions[0]
        for i in range(1, len(silent_regions)):
            if silent_regions[i] - prev_silent_sample > 1:
                if silent_regions[i] - split_points[-1] > min_silence_samples if split_points else True:
                    split_points.append(prev_silent_sample)
            prev_silent_sample = silent_regions[i]

        # Split audio based on detected silence
        chunks = []
        start = 0
        for split in split_points:
            newstart = max(0, start-500)
            newend = min(len(audio_data), split+500)
            chunks.append(audio_data[newstart:newend])
            start = split
        chunks.append(audio_data[start:])  # Add the last chunk

        self.logger("debug", f"detected chunks: {len(chunks)}")
        amount_of_chunks = len(chunks)

        for chunk_number in range(amount_of_chunks-1):
            self.logger("debug", f"chunk {chunk_number} length: {len(chunks[chunk_number])}")
            if len(chunks[chunk_number]) < 5000:
                chunks.pop(chunk_number)
                self.logger("debug", f"chunk {chunk_number} removed")
                self.logger("info", "audio to short throwing away data")

        self.logger("debug", f"chunks left over: {len(chunks)}")
        return chunks

    def proses_audio(self, input_audio):
        self.logger("debug", "proses audio")
        self.stop_log = True
        all_audio_data = np.concatenate(input_audio)
        normalized_audio = self.normalize_audio(all_audio_data)

        # self.save_audio(normalized_audio)
        # self.plot_audio_frames(normalized_audio)

        if not self.mode_continues:
            word_packets = self.split_audio(normalized_audio)

            self.logger("debug", f"word packets: {len(word_packets)}")
            if len(word_packets) > 0 and len(word_packets) < 10:
                for word in word_packets:
                    self.save_audio(word)
                    self.speech_to_text(word)
        else:
            self.logger("info", f"audio length {len(normalized_audio)/self.sample_rate} seconds")
            if len(normalized_audio) > 8000:  # todo should this be 800
                self.save_audio(normalized_audio)
                self.speech_to_text(normalized_audio)
            else:
                self.logger("error", "stopping recognition")

                # self.plot_audio_frames(word)
        self.processing = False

    def speech_to_text(self, data):
        languages = ["nl-NL", "en-US"]  # todo make this a setting

        self.logger("debug", "speech to text")

        recognizer = sr.Recognizer()
        # recognizer.recognize_google.recognize_legacy.confidance = 0.5

        # this is for analyzing the audio that was stored locally
        # if not self.mode_continues:
        #     filename = f"output/output{self.word_frame-1}.wav"
        # else:
        #     filename = "output/output.wav"
        # with sr.AudioFile(filename) as source:
        #     audio_data = recognizer.record(source)
        # todo use

        # audio_data= AudioData(source, self.sample_rate, 2)
        audio_data = sr.AudioData(data.tobytes(), self.sample_rate, 2)

        try:
            # todo make detector een optie on in te stellen
            if self.language_setting not in languages:
                self.logger("info", "language not supported current options are \"nl-NL\" and \"en-US\"")
                self.logger("info", f"\"{str(self.language_setting)}\" was given now using default language en-US")
                text = recognizer.recognize_google(audio_data, language=languages[1], with_confidence=True)
            else:
                text = recognizer.recognize_google(audio_data, language=self.language_setting, with_confidence=True)

            self.words.append(text)
            self.logger("debug", f"Recognized text: {text}")
            self.new_words = True
        except:
            self.logger("error", "can not recognize")

    def give_me_words(self):  # todo als er een andere taal is geselecteerd dan moet deze ook worden terug gegeven
        self.logger("debug", "give me words going to return words")
        self.new_words = False
        return self.words

    def plot_audio_frames(self, data):
        try:
            plt.figure(figsize=(10, 4))
            plt.plot(data)
            plt.title("Audio Frames")
            plt.xlabel("Sample Index")
            plt.ylabel("Amplitude")
            plt.savefig(f"output/plot.png")
            plt.close()
        except:
            self.logger("error", "can not plot")

    def normalize_audio(self, audio_data, target_peak=32767):
        peak = np.max(np.abs(audio_data))
        if peak == 0:
            return audio_data

        normalization_factor = target_peak / peak

        normalized_audio = (audio_data * normalization_factor).astype(np.int16)
        return normalized_audio

    def save_audio(self, audio_data):
        if self.save_to_wav:
            sample_rate = 16000
            channels = 1
            sample_width = 2

            if not self.mode_continues:
                filename = f"output/output{self.word_frame}.wav"
            else:
                filename = f"output/output{self.word_frame}.wav"

            try:
                self.logger("debug", f"Saving audio file {self.word_frame}")
                with wave.open(filename, 'wb') as wav_file:
                    wav_file.setnchannels(channels)
                    wav_file.setsampwidth(sample_width)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data.tobytes())
                    self.word_frame += 1
            except:
                self.logger("debug", "can not save file")
        else:
            self.logger("debug", "not saving audio")

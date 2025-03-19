import numpy as np
import wave
import os
import time


class SaveSpeech:
    def __init__(self, debug=False):
        self.audio_frames = []
        self.word_frame = 0
        self.stop_log = False

        self.silence_time = 3  # Changed to 3 seconds for silence detection
        self.silence_threshold = 1300
        self.silence_threshold2 = 10
        self.max_length_audio = 10

        self.sample_rate = 16000
        self.silence_counter = 0
        self.recording = False
        self.start_time = None
        self.duration = None
        self.file_path = None
        self.debug = debug

    def _debug_print(self, message):
        """Internal method for debug printing"""
        if self.debug:
            print(message)

    def record_audio(self, file_path, duration=None):
        """
        Record audio to a file for specified duration or until silence is detected

        Args:
            file_path (str): Path where to save the WAV file
            duration (float, optional): Recording duration in seconds. If None,
                                     records until silence is detected
        """
        if not file_path:
            raise ValueError("File path is required")
        # if the file path exists, delete it
        if os.path.exists(file_path):
            os.remove(file_path)

        if self.file_path is None:
            self.file_path = file_path

        # check if file exists if it does warn the user but don't overwrite it
        if os.path.exists(self.file_path):
            raise FileExistsError(
                f"File {self.file_path} already exists. Please delete it or choose a different file name."
            )

        if duration:
            self.duration = duration

        self.audio_frames = []
        self.recording = True
        self.start_time = time.time()

        self._debug_print(f"Recording started at: {self.start_time}")
        self._debug_print(f"Duration: {self.duration}")
        self._debug_print(f"Recording: {self.recording}")
        self._debug_print(f"File path: {self.file_path}")

        if self.recording:
            # This will be called from the main loop with audio data
            if duration and (time.time() - self.start_time) >= duration:
                self.save_to_file(self.file_path)
                self.recording = False
                self.audio_frames = []
                self.start_time = None
                self.duration = None
                self.file_path = None

    def process_frame(self, frame_data):
        """
        Process incoming audio frame data

        Args:
            frame_data (dict): Dictionary containing audio frame data
        """
        if not self.recording:
            return

        # Extract audio data from the dictionary
        frame_single = frame_data["data"]["body.head"]
        if frame_single is None:
            return

        audio_np = np.frombuffer(frame_single, dtype=np.int16)
        self.audio_frames.append(audio_np)

        self._debug_print(f"Duration: {time.time() - self.start_time}")

        # Check for silence if no duration was specified
        if self.duration is None:
            for packet in audio_np:
                if abs(packet) < self.silence_threshold:
                    self.silence_counter += 1
                else:
                    self.silence_counter = 0

            min_silence_samples = int(self.sample_rate * self.silence_time)
            self._debug_print(f"Silence counter: {self.silence_counter}")
            self._debug_print(f"Min silence samples: {min_silence_samples}")

            if self.silence_counter > min_silence_samples:
                self._debug_print("Silence detected, saving to file")
                self.save_to_file(self.file_path)
                self.recording = False
                self.audio_frames = []
                self.start_time = None
                self.duration = None
                self.file_path = None

        # Check for duration-based recording
        if self.duration and (time.time() - self.start_time) >= self.duration:
            self.save_to_file(self.file_path)
            self.recording = False
            self.audio_frames = []
            self.start_time = None
            self.duration = None
            self.file_path = None

    def save_to_file(self, file_path):
        """
        Save recorded audio frames to a WAV file

        Args:
            file_path (str): Path where to save the WAV file
        """
        if not self.audio_frames:
            return

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Combine all audio frames
        audio_data = np.concatenate(self.audio_frames)

        # Save as WAV file
        with wave.open(self.file_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 2 bytes per sample
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

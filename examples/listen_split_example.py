from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from time import time

import cv2 as cv
import numpy as np
import wave
import os

from alpha_mini_rug.speech_to_text import SpeechToText

# Create an instance of SpeechToText and configure parameters.
audio_processor = SpeechToText()
audio_processor.silence_time = 0.5
audio_processor.silence_threshold = 1000
audio_processor.silence_threshold2 = 100
audio_processor.logging = True  # Enable logging to see debug messages


@inlineCallbacks
def STT_using_listen_split(session):
    # Call some remote procedures to get information and configure sensors.
    info = yield session.call("rom.sensor.hearing.info")
    print("Sensor info:", info)

    sensitivity = yield session.call("rom.sensor.hearing.sensitivity")
    print("Current sensitivity:", sensitivity)

    # Optionally, adjust the sensitivity.
    yield session.call("rom.sensor.hearing.sensitivity", 1650)
    sensitivity = yield session.call("rom.sensor.hearing.sensitivity")
    print("Adjusted sensitivity:", sensitivity)

    # Set the dialogue language and ask the user to speak with clear pauses.
    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text="Please speak clearly, pausing between words.")

    print("Listening to audio using listen_split...")

    # Subscribe to the audio stream using the listen_split callback.
    yield session.subscribe(audio_processor.listen_split, "rom.sensor.hearing.stream")

    # Start the audio stream.
    yield session.call("rom.sensor.hearing.stream")

    # Main loop: periodically check if the audio processor has accumulated data
    # and then trigger processing.
    while True:
        yield sleep(0.5)
        # Call the loop method to check if enough silence was detected
        # so that the audio frames are processed (i.e. split into word chunks).
        audio_processor.loop()

        # If new words have been recognized, retrieve and print them.
        if audio_processor.new_words:
            words = audio_processor.give_me_words()
            print("Recognized words:", words)


@inlineCallbacks
def main(session, details):
    # Ensure the output directory exists.
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create an empty output file if necessary.
    output_file = os.path.join(output_dir, "output.wav")
    if not os.path.exists(output_file):
        with open(output_file, "wb") as f:
            f.write(b"")

    # Start the STT process using the listen_split function.
    yield STT_using_listen_split(session)

    # When finished, leave the session.
    session.leave()


# Configure the WAMP component. Change the URL and realm as needed.
wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["msgpack"],
            "max_retries": 0,
        }
    ],
    realm="rie.67a1cded85ba37f92bb12d56",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])

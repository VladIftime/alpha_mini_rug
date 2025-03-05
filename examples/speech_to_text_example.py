from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from time import time

import cv2 as cv
import numpy as np
import wave
import os

from alpha_mini_rug.speech_to_text import SpeechToText


audio_processor = SpeechToText()
audio_processor.silance_time = 0.5
audio_processor.silance_threshold = 1000
audio_processor.silance_threshold2 = 100
audio_processor.logging = True


@inlineCallbacks
def STT_continuous(session):
    info = yield session.call("rom.sensor.hearing.info")
    print(info)
    sensitivity = yield session.call("rom.sensor.hearing.sensitivity")
    print(sensitivity)
    yield session.call("rom.sensor.hearing.sensitivity", 1650)
    sensitivity = yield session.call("rom.sensor.hearing.sensitivity")
    print(sensitivity)

    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text="Say something")
    print("listening to audio")
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream")
    yield session.call("rom.sensor.hearing.stream")

    print("here")

    counter = 0
    while True:
        if audio_processor.new_words == False:
            yield sleep(0.2)
            counter += 1
            if counter % 100 == 0:
                audio_processor.do_speach = False
                yield session.call("rie.dialogue.say", text="Say something")
                audio_processor.do_speach = True
            try:
                # print([word_array[0][-2:],word_array[1][-2:]])
                print(word_array[-3:])
            except:
                pass
        else:
            word_array = audio_processor.give_me_words()

            try:
                # print([word_array[0][-2:],word_array[1][-2:]])
                print(word_array[-3:])
            except:
                print(word_array)
        audio_processor.loop()


@inlineCallbacks
def main(session, details):
    # Define the file path
    output_dir = "output"
    output_file = os.path.join(output_dir, "output.wav")

    # Create the directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create the file if it doesn't exist
    if not os.path.exists(output_file):
        with open(output_file, "wb") as f:
            f.write(b"")  # Write an empty byte string to create the file

    yield STT_continuous(session)

    session.leave()


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

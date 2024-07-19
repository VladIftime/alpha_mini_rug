from random import randint
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep


user_response = ""
answers_found = False


def listen_smart_question(frames):
    global user_response
    # print(frames["data"]["body"]["text"])
    # print(frames)
    if frames["data"]["body"]["final"]:
        print(frames["data"]["body"]["text"])
        user_response = frames["data"]["body"]["text"]


def find_the_answer(answer_dictionary):
    global answers_found
    answer = None
    for key in answer_dictionary.keys():  # It needs to search all values of the dictioinary, so all lists of strings and return the key
        for value in answer_dictionary[key]:
            if value in user_response:
                print("found the answer")
                answers_found = True
                answer = key

    return answers_found, answer

@inlineCallbacks
def smart_questions(session, question, answer_dictionary):
    waiting_time = 5
    number_attempts = 3
    timer = 0
    attempt = 0

    question_try_again = [
        "Sorry, can you repeat the answer?",
        "I couldn't hear the answer, can you repeat it again?",
        "I am not sure I can hear you, can you repeat?",
    ]

    yield session.call("rie.dialogue.say", text=question)

    # text = yield session.call("rie.dialogue.stt.read")
    # print("I heard ",text)

    # subscribes the asr function with the input stt stream
    yield session.subscribe(listen_smart_question, "rie.dialogue.stt.stream")
    # calls the stream. From here, the robot prints each 'final' sentence
    yield session.call("rie.dialogue.stt.stream")

    if user_response != "":
        print("user response: ", user_response)

    # loop while user did not say goodbye or bye

    while True:
        found_answer, answer = find_the_answer(answer_dictionary)
        if found_answer:
            yield session.call("rie.dialogue.stt.close")
            return answer

        timer += 0.5
        yield sleep(0.5)
        if timer >= waiting_time:
            attempt += 1
            if attempt >= number_attempts:
                yield session.call("rie.dialogue.stt.close")
                return answer
            else:
                timer = 0
                yield session.call(
                    "rie.dialogue.say", text=question_try_again[randint(0, 2)]
                )

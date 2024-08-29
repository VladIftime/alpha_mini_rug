from random import randint
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

user_response = ""
answers_found = False


def listen_smart_question(frames):
    """
    Open a stream to listen to the user
    """
    global user_response
    
    if frames["data"]["body"]["final"]:
        user_response = frames["data"]["body"]["text"]


def find_the_answer(answer_dictionary):
    """
    Searches all values of the dictionary, so all lists of strings

    Args:
        answer_dictionary (_type_): _description_
    
    Return: The answer found in the user response and the answer key    
        
    """
    global answers_found
    answer_key = None
    
    for key in answer_dictionary.keys():  
        for value in answer_dictionary[key]:
            if value in user_response:
                answers_found = True
                answer_key = key

    return answers_found, answer_key


@inlineCallbacks
def smart_questions(
    session,
    question,
    answer_dictionary,
    question_lang='en',
    answer_lang='en',
    question_try_again_lang = 'en',
    question_try_again=None,
    waiting_time=5,
    number_attempts=3,
    debug=False,
):
    """
    This function asks a question and waits for the user to respond.
    It compares the user response with the answer dictionary and returns the answer.
    The robot will ask the question again if the user response is not clear, up to 3 times.
    The robot will wait for 5 seconds for the user response.
    Args:
        session (Component): The session object.
        question (str): The question to be asked.
        answer_dictionary (dict): A dictionary with the answers.
        question_lang (str): The language the question is read
        answer_lang (str): The language the answers are expected
        question_try_again (list): A list of questions to be asked again if the user response is not clear.
        waiting_time (int): The time to wait for the user response in seconds.
        number_attempts (int): The number of attempts to ask the question again.
        debug (bool): A flag to print debug information.

    Returns:
        str: The answer found in the user response.
    """
    
    if question_try_again is None:
        question_try_again = [
            "Sorry, can you repeat the answer?",
            "I couldn't hear the answer, can you repeat it again?",
            "I am not sure I can hear you, can you repeat?",
        ]
        
    # check if the arguments are of the correct type
    if not isinstance(question, str):
        raise TypeError("question is not a string")
    if not isinstance(answer_dictionary, dict):
        raise TypeError("answer_dictionary is not a dictionary")
    # check if the dictionary contains only strings
    else:
        for key in answer_dictionary.keys():
            if not isinstance(key, str):
                raise TypeError("answer_dictionary is not a dictionary of strings")
            if not isinstance(answer_dictionary[key], list):
                raise TypeError("answer_dictionary is not a dictionary of lists")
            for value in answer_dictionary[key]:
                if not isinstance(value, str):
                    raise TypeError(
                        "answer_dictionary is not a dictionary of lists of strings"
                    )
    
    if question_try_again is not None and not isinstance(question_try_again, list):
        raise TypeError("question_try_again is not a list")
    # check if the list contains only strings
    else:
        for question in question_try_again:
            if not isinstance(question, str):
                raise TypeError("question_try_again is not a list of strings")
    if not isinstance(waiting_time, int):
        raise TypeError("waiting_time is not an integer")
    if not isinstance(number_attempts, int):
        raise TypeError("number_attempts is not an integer")
    if not isinstance(debug, bool):
        raise TypeError("debug is not a boolean")

    timer = 0
    attempt = 0

    yield session.call("rie.dialogue.say", text=question, lang=question_lang)

    # set the language for the stream and open the stream
    yield session.call("rie.dialogue.config.language", lang=answer_lang)
    yield session.subscribe(listen_smart_question, "rie.dialogue.stt.stream")
    yield session.call("rie.dialogue.stt.stream")

    if user_response != "" and debug:
        print("User response: ", user_response)

    # loop while user did not say goodbye/bye or number of attempts was reached
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
                    "rie.dialogue.say", 
                    text=question_try_again[randint(0, 2)], 
                    lang=question_try_again_lang
                )
from twisted.internet.defer import inlineCallbacks


@inlineCallbacks
def key_words(question=None, key_words=None, time=1000, debug=False):
    """
    This function asks a question and waits for the user to respond with a keyword from the list of keywords.

    Args:
        question (str): The question to be asked.
        key_words (list): A list of keywords to be checked in the user response.
        time (int): The time to wait for the user response in ms.
        debug (bool): A flag to print debug information.

    Returns:
        str: The keyword found in the user response.

    """
    global sess

    # ask question
    yield sess.call("rie.dialogue.say", text=question)
    # get user input and parse it
    user_input = yield sess.call("rie.dialogue.stt.read", time=time)
    user_response = ""
    if debug:
        print("The entire user input is: ")
        print(user_input)

    for frame in user_input:
        if frame["data"]["body"]["final"]:
            user_response = frame["data"]["body"]["text"]

    if debug:
        print("The user response is : " + user_response)
    answer_found = None

    for word in user_response.split():
        word = word.lower()
        print(word)
        if word in key_words and answer_found is None:
            answer_found = word
            break
    if debug:
        print("The keyword found: " + answer_found)
    return answer_found

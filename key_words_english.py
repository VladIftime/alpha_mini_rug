from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

# global variables
certainty_check = 0
answer_found = None
debug_flag = False
key_words_list = []


@inlineCallbacks
def key_words(session,
            question = None, 
            question_lang = 'en', 
            key_words = None, 
            key_words_lang = 'en', 
            time = 3,
            certainty = 0, 
            debug = False):
    
    global certainty_check
    global answer_found
    global debug_flag
    global key_words_list
    
     # check if the arguments are of the correct type
    if not isinstance(question, str):
        raise TypeError("question is not a string")
    if not isinstance(key_words, list):
        raise TypeError("key_words is not a list")
    # check if the list contains only strings
    else:
        for word in key_words:
            if not isinstance(word, str):
                raise TypeError("key_words is not a list of strings")
    if not isinstance(time, int):
        raise TypeError("time is not an integer")
    if not isinstance(certainty, int):
        raise TypeError("certainty is not an integer")
    if not isinstance(debug, bool):
        raise TypeError("debug is not a boolean")
    
    certainty_check = certainty
    debug_flag = debug 
    key_words_list = key_words

    # set the language and ask the question
    yield session.call("rie.dialogue.say", text=question, lang = question_lang)

    # set the language for the stream
    yield session.call("rie.dialogue.config.language", lang=key_words_lang)
    
    # start the listening stream
    yield session.subscribe(key_words_listen, "rie.dialogue.stt.stream")
    yield session.call("rie.dialogue.stt.stream")

    # record answers for the amount of time specified in seconds
    yield sleep (delay = time)
    
    # check if the answer was found
    if answer_found == None:
        print("No answer found")
    else:    
        print("The keyword found: " + answer_found)
    
    # close the stream
    session.call("rie.dialogue.stt.close")
    
    # return the found answer
    return answer_found
    

def check_words(frame_text):
    global answer_found
    global key_words_list
    
    # check if any of the key words matches the words heard
    for word in frame_text.split():
        word = word.lower()
        if word in key_words_list:
            answer_found = word
            break
        
def key_words_listen(frame):
    global debug_flag
    global certainty_check
    
    # to get the text we look for 3 conditions:
    # 1. the text found is not an empty string
    # 2. the text found is "Final" (all words heard are concatenated in one string)
    # 3. the user wants to choose words based on the "certainty"
    if (not frame["data"]["body"]["text"] == "" and
        frame["data"]["body"]["final"] and
        "certainty" in frame["data"]["body"] and 
        frame["data"]["body"]["certainty"] > certainty_check):
            
            # check the words in the text found
            check_words(frame["data"]["body"]["text"])
            
            # if the debug flag is true, it prints the all words heard
            if debug_flag:
                print("The user input is:")
                print(frame["data"]["body"]["text"])
        
@inlineCallbacks  
def main2(session, details):
    # define question 1 together with the keywords and answers
    question_colors = "What is your favorite color?"
    keywords_colors = ["red", "blue", "green", "yellow", "pink", "orange", "purple"]
    
    # call keywords function, setting the language of both question and answer
    # to English; records the answer with a certainty higher than 0.1 for 5
    # seconds; with the debug flag set to true, it prints all the words heard
    answer = yield key_words(session, 
                            question=question_colors,
                            question_lang = 'en', 
                            key_words=keywords_colors,
                            key_words_lang = 'en',
                            time=5,
                            certainty = 0.1, 
                            debug=True)
    
    if answer != None:
        string = "My favorite color is also " +  answer
    else:
        string = "Didn't understand your answer, try again later"    

    yield session.call("rie.dialogue.say", text = string)
    
    session.leave()
    
    

@inlineCallbacks
def key_words_simple(question=None, key_words=None, time=5000, debug=False):
    global sess

    # ask question
    yield sess.call("rie.dialogue.say", text=question)
    # get user input and parse it
    user_input = yield sess.call("rie.dialogue.stt.read", time=time)
    user_response = ""
    answer_found = None
    
    print(user_input)
    
    if debug:
        print("The user input is:")
        for frame in user_input:
            user_response = frame["data"]["body"]["text"]

    for frame in user_input:
            user_response = frame["data"]["body"]["text"]
            if user_response != "":
                for word in user_response.split():
                    word = word.lower()
                    print(word)
                if word in key_words and answer_found is None:
                    answer_found = word
                    break
    
    if debug:
        if answer_found == None:
            print("No answer found")
        else:    
            print("The keyword found: " + answer_found)
    
    return answer_found

@inlineCallbacks
def main(session, details):
    global sess
    sess = session

    # define question 1 together with the keywords and answers
    question_colors = "What is your favorite color?"
    keywords_colors = ["red", "blue", "green", "yellow", "pink", "orange", "purple"]
    
    yield session.subscribe(keywords_listen, "rie.dialogue.stt.stream")
    yield session.call("rie.dialogue.stt.stream")
    
    answer = yield key_words_simple_stream(question=question_colors, key_words=keywords_colors, time=5000, debug=False)
    
    print(answer)
    
    session.leave()

def second_main(session, details):
    # user_input = yield sess.call("rie.dialogue.stt.read", time=3000)
    
    # print(user_input)
    
    # for frame in user_input:
    #     # if (frame["data"]["body"]["final"]):
    #     print(frame)

    # return

    dictionary_colors = {}

    answer_red = "answer_red"
    answer_green = "answer_green"
    answer_blue = "answer_blue"
    answer_yellow = "answer_yellow"
    answer_pink = "answer_pink"
    answer_orange = "answer_orange"
    answer_purple = "answer_purple"

    dictionary_colors[answer_red] = (
        "Red is the first color that humans perceive as babies. It is often used in warning signs because it catches our attention quickly."
    )
    dictionary_colors[answer_green] = (
        "Green is the color most associated with nature. It's also the easiest color for the human eye to see."
    )
    dictionary_colors[answer_blue] = (
        "Blue is the color of the sky and the ocean. Interestingly, blue can suppress appetite, which is why it's not commonly used in food packaging"
    )
    dictionary_colors[answer_yellow] = (
        "Yellow is the most visible color in daylight, making it ideal for use in high-visibility clothing and road signs."
    )
    dictionary_colors[answer_pink] = (
        "Studies have shown that exposure to pink can have a calming effect on nerves and even reduce aggression."
    )
    dictionary_colors[answer_orange] = (
        "Orange is the color of many fruits and vegetables, which are often rich in vitamins."
    )
    dictionary_colors[answer_purple] = (
        "Purple has been historically associated with royalty and luxury because purple dye was rare and expensive to produce."
    )

    # define question 2 with the keywords and answers
    # question_season = "What is your favorite season?"
    # keywords_seasons = ["winter", "spring", "summer", "autumn"]
    # answer_general_seasons = "is a great season!"
    # answer_winter = "Winter is known for its cold weather and snowfall. This season plays a crucial role in replenishing water supplies through snowmelt, providing resources for ecosystems in the warmer months"
    # answer_spring = "Spring is often associated with renewal and new beginnings. During this season, many animals come out of hibernation, and flowers such as tulips and daffodils start to bloom."
    # answer_summer = "Summer is typically the warmest season of the year, with longer days and shorter nights. It's also the time when many fruits and vegetables reach their peak ripeness."
    # answer_autumn = "During autumn, trees prepare for winter by shedding their leaves. This happens because chlorophyll breaks down, revealing other pigments that were hidden during the growing season."

    # change the language to English
    yield session.call("rie.dialogue.config.language", lang="en")

    # set robot in neutral position, robot waves arm and says hello
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.dialogue.say.animated", text="Hello!")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")

    answer_found = yield key_words_simple(
        question=question_colors, key_words=keywords_colors, time=5000, debug = True
    )
    
    if answer_found != None:
        answer_general_colors = "Great, my favorite color is also" + answer_found
        yield session.call("rie.dialogue.say", text=answer_general_colors)

        yield session.call("rie.dialogue.say", text="Did you know that:")
        answer_string = "answer_" + answer_found
        yield session.call("rie.dialogue.say", text=dictionary_colors[answer_string])
        
    else:
        yield session.call("rie.dialogue.say", text="Sorry I didn't understand the answer. Let's try again.")
        
        answer_found = yield key_words_simple(
            question=question_colors, key_words=keywords_colors, time=5000, debug = True
        )
        
        if answer_found == None:
            yield session.call("rie.dialogue.say", text="It seems I can't hear very well today, sorry. Maybe increase the listening time.")
            session.leave()
                    
        answer_general_colors = "Great, my favorite color is also" + answer_found
        yield session.call("rie.dialogue.say", text=answer_general_colors)

        yield session.call("rie.dialogue.say", text="Did you know that:")
        answer_string = "answer_" + answer_found
        yield session.call("rie.dialogue.say", text=dictionary_colors[answer_string])
    

    session.leave()


wamp = Component(
    transports=[
        {
            "url": "ws://wamp.robotsindeklas.nl",
            "serializers": ["json"],
            "max_retries": 0,
        }
    ],
    realm="rie.66cddd6bafe50d23b76c2f24",
)

wamp.on_join(main2)

if __name__ == "__main__":
    run([wamp])

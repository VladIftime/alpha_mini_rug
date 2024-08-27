from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from collections import deque

# global variables
raw_input = deque(maxlen=20)

def on_keyword(frame):
    global sess
    if (
        "certainty" in frame["data"]["body"]
        and frame["data"]["body"]["certainty"] > 0.45
    ):
        sess.call("rie.dialogue.say", text="Ja")


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
def key_words_simple_stream(question=None, key_words=None, time=5000, debug=False):
    global sess
    global raw_input

    # ask question
    yield sess.call("rie.dialogue.say", text=question)
    # get user input and parse it
    # user_input = yield sess.call("rie.dialogue.stt.read", time=time)
    print("function before sleep")
    print(raw_input)
    yield sleep(2)
    print("function after sleep")
    print(raw_input)
    user_input = raw_input
    user_response = ""
    answer_found = None
    print(user_input)
    
    if debug:
        print("The user input is:")
        for frame in user_input:
            print(frame)

    for user_response in user_input:
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

def keywords_listen(frame):
    global raw_input
    # print("hello")
    # print(frame)
    raw_input.appendleft(frame["data"]["body"]["text"])
    # print(raw_input)

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
    realm="rie.66c6efbbafe50d23b76c0f9d",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])

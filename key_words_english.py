from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

def on_keyword(frame): 
    global sess 
    if ("certainty" in frame["data"]["body"] and 
        frame["data"]["body"]["certainty"] > 0.45): 
        sess.call("rie.dialogue.say", text= "Ja")

@inlineCallbacks
def main(session, details):
    
    global sess
    session = sess
    
    # define question 1 together with the keywords and answers
    question_colors = "What is your favorite color?"
    keywords_colors = ["red", "blue", "green", "yellow", "pink", "orange", "purple"]
    answer_general_colors = "Great, my favorite color is also"
    answer_red = "Red is the first color that humans perceive as babies. It is often used in warning signs because it catches our attention quickly."
    answer_green = "Green is the color most associated with nature. It's also the easiest color for the human eye to see."
    answer_blue = "Blue is the color of the sky and the ocean. Interestingly, blue can suppress appetite, which is why it's not commonly used in food packaging"
    answer_yellow = "Yellow is the most visible color in daylight, making it ideal for use in high-visibility clothing and road signs."
    answer_pink = "Studies have shown that exposure to pink can have a calming effect on nerves and even reduce aggression."
    answer_orange = "Orange is the color of many fruits and vegetables, which are often rich in vitamins."
    answer_purple = "Purple has been historically associated with royalty and luxury because purple dye was rare and expensive to produce."
    
    # define question 2 with the keywords and answers
    question_season = "What is your favorite season?"
    keywords_seasons = ["winter", "spring", "summer", "autumn"]
    answer_general_seasons = "is a great season!"
    answer_winter = "Winter is known for its cold weather and snowfall. This season plays a crucial role in replenishing water supplies through snowmelt, providing resources for ecosystems in the warmer months"
    answer_spring = "Spring is often associated with renewal and new beginnings. During this season, many animals come out of hibernation, and flowers such as tulips and daffodils start to bloom."
    answer_summer = "Summer is typically the warmest season of the year, with longer days and shorter nights. It's also the time when many fruits and vegetables reach their peak ripeness."
    answer_autumn = "During autumn, trees prepare for winter by shedding their leaves. This happens because chlorophyll breaks down, revealing other pigments that were hidden during the growing season."
    
    # change the language to English
    yield session.call("rie.dialogue.config.language", lang="en")

    # set robot in neutral position, robot waves arm and says hello
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.dialogue.say.animated", text="Hello!")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    
    
    # ask question about colors
    yield session.call("rie.dialogue.say", text=question_colors)
    
    # get user input and parse it
    user_input  = yield session.call("rie.dialogue.stt.read", time=10000)
    user_input = frame[["data"]["body"]["text"]] # maybe don't use frame??
    user_input = user_input.split()
    answer_color_found = None
    for word in user_input:
        if word in keywords_colors and answer_color_found is None:
            answer_color_found = word
            break
    
    yield session.call("rie.dialogue.say", text=answer_general_colors + answer_color_found)
    yield session.call("rie.dialogue.say", text="Did you know that:")
    answer_string = "answer_" + answer_color_found
    yield session.call("rie.dialogue.say", text=answer_string)
    
    session.leave()
     

            
            
    # use certainty?
    # if ("certainty" in frame["user_input"]["body"] and 
        # frame["user_input"]["body"]["certainty"] > 0.45):
    
    
    
    
    

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["json"],
		"max_retries": 0
	}],
	realm="rie.6633566bc887f6d074f02f40",
)

wamp.on_join(main)

if __name__ == "__main__":
	run([wamp])
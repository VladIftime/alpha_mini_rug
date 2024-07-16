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
    question_time_en = "Answer in Dutch what is your favorite time of the day?"
    question_time_nl = "Antwoord in het Nederlands, wat is je favoriete tijdstip van de dag?"
    keywords_time_en = ["morning", "afternoon", "night"]
    keywords_time_nl = ["ochtend", "middag", "nacht"]
    answer_general_days_en = "Your favorite time of the day is"
    answer_general_days_nl = "Je favoriete tijdstip van de dag is"
    answer_morning = "During the morning, the Earth's rotation causes the sun to rise in the east."
    answer_ochtend = "In de ochtend zorgt de rotatie van de aarde ervoor dat de zon in het oosten opkomt."
    answer_afternoon = "In the afternoon, the angle of the sun is highest in the sky, causing the shortest shadows."
    answer_middag = "In de middag staat de hoek van de zon het hoogst aan de hemel, waardoor de kortste schaduwen ontstaan."
    answer_night = "At night, the absence of sunlight allows us to see the stars and planets, that are light-years away."
    answer_nacht = "Door de afwezigheid van zonlicht kunnen we 's nachts de sterren en planeten zien die zich op lichtjaren afstand bevinden."
    
    # change the language to English
    yield session.call("rie.dialogue.config.language", lang="en")

    # set robot in neutral position, robot waves arm and says hello
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    session.call("rie.dialogue.say.animated", text="Hello!")
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    
    
    # ask question about colors
    yield session.call("rie.dialogue.say", text="We will practice some words in Dutch.")
    yield session.call("rie.dialogue.say", text="First I'll say the sentence in English, followed by the translation in Dutch.")
    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text=question_time_en)
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.say", text=question_time_nl)
    
    # get user input and parse it
    user_input  = yield session.call("rie.dialogue.stt.read", time=10000)
    user_input = frame[["data"]["body"]["text"]] # maybe don't use frame??
    user_input = user_input.split()
    
    answer_time_found_nl = None
    answer_time_found_en = None
    
    for word in user_input:
        if word in keywords_time_nl and answer_time_found_nl is None:
            answer_time_found_nl = word
            answer_time_found_en = keywords_time_en[keywords_time_nl.index(word)]
            break
    
    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text=answer_general_days_en + answer_time_found_en)
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.say", text=answer_general_days_nl + answer_time_found_nl)
    
    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text="Did you know that:")
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.say", text="Wist je dat:")
    
    answer_string_en = "answer_" + answer_time_found_en
    answer_string_nl = "answer_" + answer_time_found_nl
    
    yield session.call("rie.dialogue.config.language", lang="en")
    yield session.call("rie.dialogue.say", text=answer_string_en)
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.say", text=answer_string_nl)
    
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
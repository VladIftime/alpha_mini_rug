from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

def collision_models():
	return

@inlineCallbacks
def main(session, details):
    collision_models()
    
    session.leave()

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
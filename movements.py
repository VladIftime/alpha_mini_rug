from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

# dictionary of movements:
joints = {
    "body.head.yaw": (-0.875, 0.875), 					# 0.3
    "body.head.roll": (-0.175, 0.175), 					# 0.2
    "body.head.pitch": (-0.175, 0.175), 				# 0.2
    "body.arms.right.upper.pitch": (-2.60, 1.60),		# 0.8 
    "body.arms.right.lower.roll": (-1.75, 0.000065), 	# 0.6
    "body.arms.left.upper.pitch": (-2.60, 1.60),		# 0.8
    "body.arms.left.lower.roll": (-1.75, 0.000065),		# 0.6
    "body.torso.yaw": (-0.875, 0.875),					# 0.5
    "body.legs.right.upper.pitch": (-1.75, 1.75),		# 0.8 + add warning about falling somehow
    "body.legs.right.lower.pitch": (-1.75, 1.75),		# 0.6 + add warning about falling somehow
    "body.legs.right.foot.roll": (-0.850, 0.250),		# 0.5 + add warning about falling somehow
    "body.legs.left.upper.pitch": (-1.75, 1.75),		# 0.8 + add warning about falling somehow
    "body.legs.left.lower.pitch": (-1.75, 1.75),		# 0.6 + add warning about falling somehow
    "body.legs.left.foot.roll": (-0.850, 0.250)			# 0.5 + add warning about falling somehow
}

# check if the set angles of one frame are withing boundaries
def check_angle_set_value(frame_joints_dic):
	for joint in frame_joints_dic:
		if not joint in joints_dic:
			raise ValueError(joint + " is not a valid joint name")
		else:
			if not joints_dic[joint][0] <= frame_joints_dic[joint] <= joints_dic[joint][1]:
				raise ValueError("The angle selected for joint " + joint + " is out of bounds")

def calculate_required_time(current_pos, target_pos, min_angle, max_angle, min_time):
	# calculate the total range of motion
	total_range = abs(max_angle - min_angle)
	
	# calculate the movement range required
	movement_range = abs(target_pos - current_pos)
	
	# calculate the proportional time
	proportional_time = (movement_range / total_range) * min_time
	
	return proportional_time

# if you don't want to provide a custom time, you can set "time" to None and by default all movements will be executes 1 seconds apart

# the minimum time between any movements is proportional to the angle of movement
# @inlineCallbacks
def perform_action_standard_time(frames, mode = "linear", sync = True, force = False):
    
    if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
        raise TypeError("frames is not a list of tuples, it needs to follow the structure [{\"time\": (int), \"data\": {name_joints (string): position_joint (float), ...}}")
    
    if not isinstance(mode, str):
        raise TypeError("mode is not a string, choose one of the following \"linear\", \"last\", \"none\"")

    if not isinstance(sync, bool):
        raise TypeError("sync is not a boolean, choose one of the following True, False")

    if not isinstance(force, bool):
        raise TypeError("force is not a boolean, choose one of the following True, False")
    
    # check the first frame
    if frames[0]["time"] == None or frames[0]["time"] < 1000:
        frames[0]["time"] = 1000
        
    
    for i in range(len(frames) - 1):
        frame1 = frames[i]
        frame2 = frames[i + 1]
        
        if frame2["time"] != None and frame2["time"] - frame1["time"] < 1000:    
            print("ValueError: Some movements are set too fast, for safety reasons they are set now at 1 second")
            frame2["time"] += 1000 - (frame2["time"] - frame1["time"])
        else:
            frame2["time"] = frame1["time"] + 1000 
               
    print(frames)
    print(mode)
    print(sync)
    print(force)         
            
    # session.call("rom.actuator.motor.write", frames, mode, sync, force=True)

# the minimum time between any movements is set to 1 second
# @inlineCallbacks
def perform_action_proportional_time(frames, mode = "linear", sync = True, force = False):
    
    if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
        raise TypeError("frames is not a list of tuples, it needs to follow the structure [{\"time\": (int), \"data\": {name_joints (string): position_joint (float), ...}}")
    
    if not isinstance(mode, str):
        raise TypeError("mode is not a string, choose one of the following \"linear\", \"last\", \"none\"")

    if not isinstance(sync, bool):
        raise TypeError("sync is not a boolean, choose one of the following True, False")

    if not isinstance(force, bool):
        raise TypeError("force is not a boolean, choose one of the following True, False")
    
    # check the joints of the first frame
    print(frames[0]["data"])
    
    for key, value in frames[0]["data"].items():
        print(key)
        print(value)
        if key in joints:
             print(joints[key])
        else:
            print("ValueError: " + str(key) + " is not a valid joint name")     

    # if frames[0]["time"] == None or frames[0]["time"] < 1000:
    #     frames[0]["time"] = 1000
      
    # for i in range(len(frames) - 1):
    #     frame1 = frames[i]
    #     frame2 = frames[i + 1]
        
    #     if frame2["time"] != None and frame2["time"] - frame1["time"] < 1000:    
    #         print("ValueError: Some movements are set too fast, for safety reasons they are set now at 1 second")
    #         frame2["time"] += 1000 - (frame2["time"] - frame1["time"])
    #     else:
    #         frame2["time"] = frame1["time"] + 1000 
               
    # print(frames)
    # print(mode)
    # print(sync)
    # print(force)         
            
    # session.call("rom.actuator.motor.write", frames, mode, sync, force=True)
    
    
def main():
    frames = [{"time": None, "data": {"body.arms.left.lower.roll": -1.70, "body.arms.right.lower.roll": -1.70}},
 			  {"time": None, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]
    perform_action_proportional_time(frames)

if __name__ == "__main__":
    main()
    
                


# @inlineCallbacks
# def main(session, details):
    
#     frames = [{"time": 500, "data": {"body.arms.left.lower.roll": -1.70, "body.arms.right.lower.roll": -1.70}},
# 			  {"time": 2000, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]
    
#     yield perform_action(session, frames)
    
#     session.leave()

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["json"],
		"max_retries": 0
	}],
	realm="rie.66c5c090afe50d23b76c099e",
)

wamp.on_join(main)

# if __name__ == "__main__":
# 	run([wamp])
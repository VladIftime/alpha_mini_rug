from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

# dictionary of joint angles 
# joint name: (min_angle, max_angle, minimum time from 0 to min or max)":
joints_dic = {
	"body.head.yaw":                (-0.874, 0.874, 300), 	# 0.3
	"body.head.roll":               (-0.174, 0.174, 200), 	# 0.2
	"body.head.pitch":              (-0.174, 0.174, 200), 	# 0.2
	"body.arms.right.upper.pitch":  (-2.59, 1.59, 800),		# 0.8 
	"body.arms.right.lower.roll":   (-1.74, 0.000064, 600), # 0.6
	"body.arms.left.upper.pitch":   (-2.59, 1.59, 800),		# 0.8
	"body.arms.left.lower.roll":    (-1.74, 0.000064, 600),	# 0.6
	"body.torso.yaw":               (-0.874, 0.874, 500),	# 0.5
	"body.legs.right.upper.pitch":  (-1.74, 1.74, 800),		# 0.8 + add warning about falling somehow
	"body.legs.right.lower.pitch":  (-1.74, 1.74, 600),		# 0.6 + add warning about falling somehow
	"body.legs.right.foot.roll":    (-0.849, 0.249, 500),	# 0.5 + add warning about falling somehow
	"body.legs.left.upper.pitch":   (-1.74, 1.74, 800),		# 0.8 + add warning about falling somehow
	"body.legs.left.lower.pitch":   (-1.74, 1.74, 600),		# 0.6 + add warning about falling somehow
	"body.legs.left.foot.roll":     (-0.849, 0.249, 500)    # 0.5 + add warning about falling somehow
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
@inlineCallbacks
def perform_action_standard_time(session, frames, mode = "linear", sync = True, force = False):
	
	if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
		raise TypeError("frames is not a list of tuples, it needs to follow the structure [{\"time\": (int), \"data\": {name_joints (string): position_joint (float), ...}}")
	
	if not isinstance(mode, str):
		raise TypeError("mode is not a string, choose one of the following \"linear\", \"last\", \"none\"")

	if not isinstance(sync, bool):
		raise TypeError("sync is not a boolean, choose one of the following True, False")

	if not isinstance(force, bool):
		raise TypeError("force is not a boolean, choose one of the following True, False")
	
	# check if the joint angle is within boundaries
	check_angle_set_value(frames[0]["data"])
	
	# check if the time set for the first frame is less than 1 second
	if frames[0]["time"] == None or frames[0]["time"] < 1000:
		frames[0]["time"] = 1000
		
	# iterate over all frames and compare them two by two    
	for idx in range(len(frames) - 1):
		frame1 = frames[idx]
		frame2 = frames[idx + 1]
		
		# check if the joint angle is within boundaries
		check_angle_set_value(frame2["data"])
		
		# check if the time set is less than 1 second
		if frame2["time"] != None and frame2["time"] - frame1["time"] < 1000:    
			print("ValueError: Some movements are set too fast, for safety reasons they are set now at 1 second")
			frame2["time"] += 1000 - (frame2["time"] - frame1["time"])
		else:
			frame2["time"] = frame1["time"] + 1000       
			
	session.call("rom.actuator.motor.write", frames, mode, sync, force=True)

# the minimum time between any movements is proportional to the angle of movement
@inlineCallbacks
def perform_action_proportional_time(session, frames, mode = "linear", sync = True, force = False):
	
	if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
		raise TypeError("frames is not a list of tuples, it needs to follow the structure [{\"time\": (int), \"data\": {name_joints (string): position_joint (float), ...}}")
	
	if not isinstance(mode, str):
		raise TypeError("mode is not a string, choose one of the following \"linear\", \"last\", \"none\"")

	if not isinstance(sync, bool):
		raise TypeError("sync is not a boolean, choose one of the following True, False")

	if not isinstance(force, bool):
		raise TypeError("force is not a boolean, choose one of the following True, False")
	
 	# check the joints and angles of the first frame
	check_angle_set_value(frames[0]["data"])
 
	# get the joints angle at this time
	current_position = yield session.call("rom.sensor.proprio.read")
	# print(current_position[0]["data"])
	
 	# check the time set of the first frame
	for joint, target_position in frames[0]["data"].items():
		minimum_required_time = calculate_required_time(current_position[0]["data"][joint], 
													target_position,
													joints_dic[joint][0],
													joints_dic[joint][1],
													joints_dic[joint][2])
		
		minimum_required_time = round(minimum_required_time,2)
		print(minimum_required_time)
		if frames[0]["time"] == None or minimum_required_time > frames[0]["time"]:
			print("The time of frame 0 was changed from " + str(frames[0]["time"]) + " to " + str(minimum_required_time))
			frames[0]["time"] = minimum_required_time

	for idx in range(len(frames) - 1):
		frame1 = frames[idx]
		frame2 = frames[idx + 1]
  
		for joint, target_position in frame2["data"].items():
			minimum_required_time = calculate_required_time(frame1["data"][joint], 
															target_position,
															joints_dic[joint][0],
															joints_dic[joint][1],
															joints_dic[joint][2])
			minimum_required_time = round(minimum_required_time,2)
		if frame2["time"] == None or minimum_required_time > frame2["time"]:    
			print("The time of frame " + str(idx + 1) +  " was changed from " + str(frame2["time"]) + " to " + str(minimum_required_time))
			frame2["time"] = minimum_required_time
			   
	# print(frames)
	# print(mode)
	# print(sync)
	# print(force)         
	print("call")
	session.call("rom.actuator.motor.write", frames, mode, sync, force=True)
	
	
# def main():
# 	frames = [{"time": None, "data": {"body.arms.left.lower.roll": -1.70, "body.arms.right.lower.roll": -1.70}},
#  			  {"time": None, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]
		
# 	perform_action_proportional_time(frames)

# if __name__ == "__main__":
# 	main()

@inlineCallbacks
def main(session, details):
	
    frames = [{"time": 500, "data": {"body.arms.left.lower.roll": -1.70, "body.arms.right.lower.roll": -1.70}},
			  {"time": 2000, "data": {"body.arms.left.lower.roll": 0, "body.arms.right.lower.roll": 0}}]
	
    # yield perform_action_proportional_time(session, frames)
    print("call")
    yield session.call("rom.actuator.motor.write", frames, force=True)
	
    session.leave()

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["json"],
		"max_retries": 0
	}],
	realm="rie.66c5c090afe50d23b76c099e",
)

wamp.on_join(main)

if __name__ == "__main__":
    run(wamp)
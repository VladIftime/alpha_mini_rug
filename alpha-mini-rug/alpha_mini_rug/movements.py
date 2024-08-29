from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

''' 
    Dictionary of joint angles
    joint name: (min_angle, max_angle, minimum time to perform a full movement from min to max)":
'''
joints_dic = {
    "body.head.yaw": (-0.874, 0.874, 600), 
    "body.head.roll": (-0.174, 0.174, 400), 
    "body.head.pitch": (-0.174, 0.174, 400),
    "body.arms.right.upper.pitch": (-2.59, 1.59, 1800),
    "body.arms.right.lower.roll": (-1.74, 0.000064, 1200),
    "body.arms.left.upper.pitch": (-2.59, 1.59, 1600),
    "body.arms.left.lower.roll": (-1.74, 0.000064, 1200),
    "body.torso.yaw": (-0.874, 0.874, 1000),
    "body.legs.right.upper.pitch": (-1.74, 1.74, 1600),
    "body.legs.right.lower.pitch": (-1.74, 1.74, 1200), 
    "body.legs.right.foot.roll": (-0.849, 0.249, 1000), 
    "body.legs.left.upper.pitch": (-1.74, 1.74, 1600), 
    "body.legs.left.lower.pitch": (-1.74, 1.74, 1200), 
    "body.legs.left.foot.roll": (-0.849, 0.249, 1000),
}

def check_angle_set_value(frame_joints_dic):
    """ 
    Check if the name of the joints are specified correctly and the set angles are within the hardware boundaries
    
    Args:
        frame_joints_dic (dict): Dictionary of all joint names and angle limits
        
    Returns:
        None    
    """
    for joint in frame_joints_dic:
        if not joint in joints_dic:
            raise ValueError(joint + " is not a valid joint name")
        else:
            if (
                not joints_dic[joint][0]
                <= frame_joints_dic[joint]
                <= joints_dic[joint][1]
            ):
                raise ValueError(
                    "The angle selected for joint " + joint + " is out of bounds"
                )

def calculate_required_time(current_pos, target_pos, min_angle, max_angle, min_time):
    ''' 
        Check if the set time is too quick and adjust it proportional to the angle of movement
        
        Return: the proportional time in ms
    '''
    # calculate the total range of motion
    total_range = abs(max_angle - min_angle)

    # calculate the movement range required
    movement_range = abs(target_pos - current_pos)

    # calculate the proportional time
    proportional_time = (movement_range / total_range) * min_time

    return proportional_time

@inlineCallbacks
def perform_movement(
    session, frames, mode="linear", sync=True, force=False
):
    """
    This function performs a movement with the robot's joints. The time of each frame is calculated based on the proportional time of the movement.

    Args:
        session (Component): The session object.
        frames (list): A list of dictionaries with the time and data of the joints to be moved.
        mode (str): The mode of the movement. Choose one of the following: "linear", "last", "none".
        sync (bool): A flag to synchronize the movement of the joints.
        force (bool): A flag to force the movement of the joints.

    Returns:
        None
    """
    
    # check if the arguments are of the correct type
    if not isinstance(frames, list) and all(isinstance(item, dict) for item in frames):
        raise TypeError('frames is not a list of tuples')
    if not isinstance(mode, str):
        raise TypeError('mode is not a string')
    if not isinstance(sync, bool):
        raise TypeError('sync is not a boolean')
    if not isinstance(force, bool):
        raise TypeError('force is not a boolean')

    # get the joints angle at this time
    current_position = yield session.call("rom.sensor.proprio.read")

    # check the joints name, angles and times
    check_angle_set_value(frames[0]["data"])
    for joint, target_position in frames[0]["data"].items():
        minimum_required_time = calculate_required_time(
            current_position[0]["data"][joint],
            target_position,
            joints_dic[joint][0],
            joints_dic[joint][1],
            joints_dic[joint][2],
        )

        minimum_required_time = round(minimum_required_time, 2)
        if frames[0]["time"] == None or minimum_required_time > frames[0]["time"]:
            print(
                "The time of frame 0 was changed from "
                + str(frames[0]["time"])
                + " to "
                + str(minimum_required_time)
            )
            frames[0]["time"] = minimum_required_time

    for idx in range(len(frames) - 1):
        frame1 = frames[idx]
        frame2 = frames[idx + 1]

        for joint, target_position in frame2["data"].items():
            minimum_required_time = calculate_required_time(
                frame1["data"][joint],
                target_position,
                joints_dic[joint][0],
                joints_dic[joint][1],
                joints_dic[joint][2],
            )
            minimum_required_time = round(minimum_required_time, 2)
        if frame2["time"] == None or minimum_required_time > frame2["time"]:
            print(
                "The time of frame "
                + str(idx + 1)
                + " was changed from "
                + str(frame2["time"])
                + " to "
                + str(minimum_required_time)
            )
            frame2["time"] = minimum_required_time

    session.call("rom.actuator.motor.write", frames=frames, mode=mode, sync=sync, force=True)

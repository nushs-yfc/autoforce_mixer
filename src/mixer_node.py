#!/usr/bin/env python
import rospy
from mixer_node.msg import NodeWeightArray
from geometry_msgs.msg import Transform

inputs = {}

def input_callback_make(name):
    def input_callback(data):
        inputs[name] = [data, inputs[name][1]]
    return input_callback

def controller_callback(data):
    for datum in data.node_weights:
        try:
            inputs[datum.name] = [inputs[datum.name][0], datum.weight]
        except:
            rospy.Subscriber(datum.name, Transform, input_callback_make(datum.name))
            inputs[datum.name] = [0, datum.weight]

def get_part(x, i, i2):
    if i == 0:
        x = x.translation
        if i2 == 0:
            return x.x
        else if i2 == 1:
            return x.y
        else if i2 == 2:
            return x.z
    else if i == 1:
        x = x.rotation
        if i2 == 0:
            return x.x
        else if i2 == 1:
            return x.y
        else if i2 == 2:
            return x.z
        else if i2 == 3:
            return x.w
    return None

def set_part(x, v, i, i2):
    if i == 0:
        x = x.translation
        if i2 == 0:
            x.x = v
        else if i2 == 1:
            x.y = v
        else if i2 == 2:
            x.z = v
    else if i == 1:
        x = x.rotation
        if i2 == 0:
            x.x = v
        else if i2 == 1:
            x.y = v
        else if i2 == 2:
            x.z = v
        else if i2 == 3:
            x.w = v
    return x

def main():
    pub = rospy.Publisher('mixer_out', Transform, queue_size=10)

    rospy.init_node('mixer')
    rate = rospy.Rate(10)

    rospy.Subscriber('autoforce_offb_controller', NodeWeightArray, controller_callback)
    
    while not rospy.is_shutdown():
        output = Transform()
        idxs = [(i, i2) for i2 in range(i+3) for i in range(2)]
        for i, i2 in idxs:
            total = sum([get_part(input[key], i, i2) for key in inputs.keys()])
            out = sum([get_part(input[key], i, i2)/total * get_part(inputs[key], i, i2) for key in inputs.key()])
            output = set_part(output, out, i, i2)
        pub.publish(output)
        rate.sleep()

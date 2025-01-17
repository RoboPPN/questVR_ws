#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from oculus_reader import OculusReader
from tf.transformations import quaternion_from_matrix

import rospy
import tf2_ros
import numpy as np
import geometry_msgs.msg
from pinocchio_vr_single_piper import Arm_IK
from tools import MATHTOOLS

from piper_control import PIPER

class VR:
    def __init__(self):
        self.piper_control = PIPER()

        # 运算工具包
        self.tools = MATHTOOLS()

        # 机械臂逆解
        self.inverse_solution = Arm_IK()

    # 调整矩阵函数
    def adjustment_matrix(self,transform):
        """
        input
            transform: 4x4 numpy array
        output
            4x4 numpy array
        """
        # 输入验证
        if transform.shape != (4, 4):
            raise ValueError("Input transform must be a 4x4 numpy array.")
        
        adj_mat = np.array([
            [0,0,-1,0],
            [-1,0,0,0],
            [0,1,0,0],
            [0,0,0,1]
        ])
        
        r_adj = self.tools.xyzrpy2Mat(0,0,0,   -np.pi , 0, -3.1415926/2)
        
        # 矩阵乘法，调整 transform
        transform = adj_mat @ transform  # 使用@运算符进行矩阵乘法
        
        # 再进行一次矩阵乘法，这次是调整坐标轴方向
        transform = np.dot(transform, r_adj)  # 使用@运算符进行矩阵乘法  

        #or
        
        # transform =  transform @ r_adj
        
        return transform

    def publish_transform(self,transform, name):
        translation = transform[:3, 3]

        br = tf2_ros.TransformBroadcaster()
        t = geometry_msgs.msg.TransformStamped()

        t.header.stamp = rospy.Time.now()
        t.header.frame_id = 'vr_device'
        t.child_frame_id = name
        t.transform.translation.x = translation[0]
        t.transform.translation.y = translation[1]
        t.transform.translation.z = translation[2]

        quat = quaternion_from_matrix(transform)
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]

        br.sendTransform(t)

    # 增量式控制
    def calc_pose_incre(self,base_pose, pose_data):
        begin_matrix = self.tools.xyzrpy2Mat(base_pose[0], base_pose[1], base_pose[2],
                                                    base_pose[3], base_pose[4], base_pose[5])
        zero_matrix = self.tools.xyzrpy2Mat(0.05, 0.0, 0.2, 0, 0, 0)
        end_matrix = self.tools.xyzrpy2Mat(pose_data[0], pose_data[1], pose_data[2],
                                                pose_data[3], pose_data[4], pose_data[5])
        result_matrix = np.dot(zero_matrix, np.dot(np.linalg.inv(begin_matrix), end_matrix))
        xyzrpy = self.tools.mat2xyzrpy(result_matrix)
        return xyzrpy
    
    def Run(self):
        # 这里可选为 WIFI连接 或 USB连接
        # oculus_reader = OculusReader(ip_address='10.12.11.14')    #  WIFI连接
        oculus_reader = OculusReader()                              #  USB连接
        rospy.init_node('oculus_reader')

        rate = rospy.Rate(50)
        
        base_RR = [0.05,0.0,0.2,0,0,0]
        
        while not rospy.is_shutdown():
            rate.sleep()
            transformations, buttons = oculus_reader.get_transformations_and_buttons()
            if 'r' not in transformations :
                continue

            # 进行调整
            transformations['r'] = self.adjustment_matrix(transformations['r'])
            
            right_controller_pose = transformations['r']
            
            # 打印信息手柄信息
            # print('transformations', transformations)
            # print('buttons', buttons)
            
            self.publish_transform(right_controller_pose, 'right_hand')
            
            RR = self.tools.matrix2Pose(transformations['r'])
                
            if buttons['A'] == True :
                # 按下A键后，机械臂回到初始点位并且记录 右 坐标原点
                self.piper_control.left_init_pose()
                base_RR = self.tools.matrix2Pose(transformations['r'])
                        
            RR_ = self.calc_pose_incre(base_RR,RR)
            
            r_gripper_value = buttons['rightTrig'][0] * 0.07 
            
            self.inverse_solution.get_ik_solution(RR_[0],RR_[1],RR_[2],RR_[3],RR_[4],RR_[5],r_gripper_value)

if __name__ == '__main__':
    vr = VR()
    vr.Run()
    

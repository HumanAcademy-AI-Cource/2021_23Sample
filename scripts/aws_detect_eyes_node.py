#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 必要なライブラリをインポート
import rospy
import cv2
import subprocess
import roslib.packages
import boto3
import os
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import aws_detect_eyes


class DetectEyes(object):
    def __init__(self):
        rospy.Subscriber("/image_raw", Image, self.imageCB)
        self.image = None
        self.enable_process = 0
        self.pkg_path = roslib.packages.get_pkg_dir("myface_recognition")

        # 画像の保存先ディレクトリのパスを定義
        self.image_path = roslib.packages.get_pkg_dir('myface_recognition') + '/scripts/images/'
        # ディレクトリがない場合は新しく作成
        if not os.path.isdir(roslib.packages.get_pkg_dir('myface_recognition') + '/scripts/images/'):
            os.mkdir(roslib.packages.get_pkg_dir('myface_recognition') + '/scripts/images/')


    def process(self):
        target_file = self.pkg_path + "/scripts/images/detect_eyes_camera.jpg"
        cv2.imwrite(target_file, self.image)
        
        # 画像から目の状態を検出
        detect_text = aws_detect_eyes.aws_detect_eyes(target_file)
        print("○ 検出した目の状態")
        if detect_text == "Open":
            rospy.loginfo("目が開いています。")
        if detect_text == "Closed":
            rospy.loginfo("目を閉じています。")
        if detect_text == "":
            rospy.loginfo("目を検出できませんでした。")

        self.infomessage()


    def imageCB(self, msg):
        # カメラ画像を受け取る
        self.image = CvBridge().imgmsg_to_cv2(msg, "bgr8")
        cv2.imshow('Camera', cv2.resize(self.image, dsize=None, fx=0.75, fy=0.75))
        # キー判定をする
        key = cv2.waitKey(1)
        if key == ord('s'):
            self.enable_process = 1
        if key == ord('e'):
            self.enable_process = 2


    def infomessage(self):
        print("=======================================================================")
        print("目が開いているか検出するシステム")
        print("  - カメラウィンドウを選択した状態で[s]キーを押すと検出開始")
        print("  - [e]キーを押すと終了します。")
        print("=======================================================================")


    def run(self):
        # 案内用のメッセージを表示
        self.infomessage()
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            if self.enable_process == 1:
                self.enable_process = 0
                self.process()
            if self.enable_process == 2:
                self.enable_process = 0
                print("３秒後にプログラムを終了します。")
                rospy.sleep(3)
                sys.exit(0)
            rate.sleep()

if __name__ == '__main__':
    # ノードを宣言
    rospy.init_node('aws_detect_eyes_node')
    DetectEyes().run()

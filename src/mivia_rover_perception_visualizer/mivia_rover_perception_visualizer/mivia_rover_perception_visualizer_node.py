#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rclpy
from rclpy.node import Node

### ROS message imports
from sensor_msgs.msg import Image
from zed_msgs.msg import ObjectsStamped

import cv2
import numpy as np
import cv_bridge

from message_filters import Subscriber, ApproximateTimeSynchronizer

class MiviaRoverPerceptionVisualizerNode(Node):

    def __init__(self) -> None:
        """
        This node is responsible for displaying objects detected by the zed2 stereo camera.
        """
        super().__init__("mivia_rover_perception_visualizer_node")

        self.bridge = cv_bridge.CvBridge()

        # Synchronized subscribers
        self.image_sub = Subscriber(self, Image, "~/input/image_raw")
        self.obj_sub   = Subscriber(self, ObjectsStamped, "~/input/objects")

        self.ts = ApproximateTimeSynchronizer(
            [self.image_sub, self.obj_sub],
            queue_size=10,
            slop=0.1
        )
        self.ts.registerCallback(self.callback)

        # Publisher for processed image
        self.pub = self.create_publisher(Image, "~/output/image", 10)

        self.get_logger().info("Perception Visualizer Node initialized.")


    def draw_label(self, image: np.ndarray, text: str, pos: tuple, bg_color: tuple=(255, 255, 255), text_color: tuple=(0, 0, 0), font: int=cv2.FONT_HERSHEY_SIMPLEX, font_scale: float=0.5, thickness: int=1) -> None:
        """Draw a label with background on the image at the specified position."""
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_w, text_h = text_size
        x, y = pos
        cv2.rectangle(image, (x, y), (x + text_w + 4, y + text_h + 4), bg_color, -1)
        cv2.putText(image, text, (x + 2, y + text_h + 2), font, font_scale, text_color, thickness)

    def callback(self, img_msg: Image, obj_msg: ObjectsStamped) -> None:
        try:
            cv_image = self.bridge.imgmsg_to_cv2(img_msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Error CvBridge: {e}")
            return

        ### Draw bounding boxes
        for obj in obj_msg.objects:

            corners = obj.bounding_box_2d.corners
            if not corners:
                continue

            x_min = int(corners[0].kp[0])
            y_min = int(corners[0].kp[1])
            x_max = int(corners[2].kp[0])
            y_max = int(corners[2].kp[1])

            label = obj.label
            cv2.rectangle(cv_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

            # 3D world position
            px, py, pz = obj.position

            text = f"{label} ({px:.2f},{py:.2f},{pz:.2f})"
            if obj.label_id >= 0:
                text = f"ID: {obj.label_id} " + text
            self.draw_label(cv_image, text, (x_min, y_min))

        ### Publish annotated image
        try:
            out_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            out_msg.header = img_msg.header
            self.pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f"Error publish: {e}")
            return
        

def main(args=None):
    rclpy.init(args=args)
    node = MiviaRoverPerceptionVisualizerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

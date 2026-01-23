# mivia_rover_perception

ROS2 workspace dedicated to the **perception module** for the MIVIA rover.
It detects objects in the scene, using a ZED2 Stereo Camera, and then estimates the position of those objects.  
> [!NOTE]
> In this workspace there is only the node to display the perception output, since the algorithm is executed by the ZED2 ros2 wrapper (which you can find [here](../../../mivia_rover_sensing/src/zed-ros2-wrapper/)).

## Workspace Structure

```

└── src
└────  mivia_rover_perception

```

## Requirements

- ROS 2 **Humble**
- Python ≥ 3.10
- `zed_msgs`
- `message_filters`
- `OpenCV`

---

## Build Instructions

From the root of the repository:

```bash
cd ~/mivia_rover
colcon build --symlink-install
source install/setup.bash
```

---

## Packages Overview

### `mivia_rover_perception`

This node is responsible for drawing the 2D bounding boxes output by a detector and drawing them on the RGB image.

To view the output of the perception module, run this command:
```bash
cd ~/mivia_rover
source install/setup.bash
ros2 launch mivia_rover_perception mivia_rover_perception_node
```

> [!IMPORTANT]
> To view the output you **MUST** first launch the [ZED wrapper node](../../../mivia_rover_sensing/src/zed-ros2-wrapper/zed_wrapper/launch/zed_camera.launch.py).
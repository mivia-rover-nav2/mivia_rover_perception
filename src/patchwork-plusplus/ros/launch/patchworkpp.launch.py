from launch import LaunchDescription
from launch.substitutions import (LaunchConfiguration)
from launch_ros.actions import Node


# This configuration parameters are not exposed thorugh the launch system, meaning you can't modify
# those throw the ros launch CLI. If you need to change these values, you could write your own
# launch file and modify the 'parameters=' block from the Node class.
class config:
    # TBU. Examples are as follows:
    max_range: float = 80.0
    # deskew: bool = False


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # tf tree configuration, these are the likely 3 parameters to change and nothing else
    base_frame = LaunchConfiguration("base_frame", default="base_link")

    # Patchwork++ node
    patchworkpp_node = Node(
        package="patchworkpp",
        executable="patchworkpp_node",
        name="patchworkpp_node",
        output="screen",
        remappings=[
            ("pointcloud_topic", '/zed/zed_node/point_cloud/cloud_registered'),
        ],
        parameters=[
            {
                # ROS node configuration
                "base_frame": base_frame,
                "use_sim_time": use_sim_time,
                # Patchwork++ configuration
                "sensor_height": 0.24,
                "num_iter": 4,  # Number of iterations for ground plane estimation using PCA.
                "num_lpr": 30,  # Maximum number of points to be selected as lowest points representative.
                "num_min_pts": 20,  # Minimum number of points to be estimated as ground plane in each patch.
                "th_seeds": 0.4,
                # threshold for lowest point representatives using in initial seeds selection of ground points.
                "th_dist": 0.3,  # threshold for thickness of ground.
                "th_seeds_v": 0.25,
                # threshold for lowest point representatives using in initial seeds selection of vertical structural points.
                "th_dist_v": 1.0,  # threshold for thickness of vertical structure.
                "max_range": 7.0,  # max_range of ground estimation area
                "min_range": 0.1,  # min_range of ground estimation area
                "uprightness_thr": 0.70,
                # threshold of uprightness using in Ground Likelihood Estimation(GLE). Please refer paper for more information about GLE.
                "verbose": True,  # display verbose info
                "filter_high_z": True,  # filter points higher than sensor height
                "th_filter_high_z": 0.35,  # threshold for filtering points higher than sensor height
            }
        ],
    )

    return LaunchDescription(
        [
            patchworkpp_node,
        ]
    )

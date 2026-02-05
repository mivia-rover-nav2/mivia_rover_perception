from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    perception_visualizer_launch_file_path = os.path.join(
        get_package_share_directory('mivia_rover_perception_visualizer'),
        'launch',
        'mivia_rover_perception_visualizer_node.launch.py'
    )
    patchworkpp_launch_file_path = os.path.join(
        get_package_share_directory('patchworkpp'),
        'launch',
        'patchworkpp.launch.py'
    )

    perception_visualizer = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            perception_visualizer_launch_file_path
            )
        )
    patchworkpp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            patchworkpp_launch_file_path
            )
        )

    return LaunchDescription([
        perception_visualizer,
        patchworkpp
    ])
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    perception_visualizer = Node(
        package="mivia_rover_perception_visualizer",
        executable="mivia_rover_perception_visualizer_node",
        name="mivia_rover_perception_visualizer_node",
        output="screen",
        remappings=[
            ("~/input/image_raw",  "/zed/zed_node/rgb/color/rect/image"),
            ("~/input/objects",    "/zed/zed_node/obj_det/objects"),
            ("~/output/image",     "/perception/debug/image"),
        ],
        parameters=[
            {
                "use_sim_time": False
            }
        ]
    )

    return LaunchDescription([
        perception_visualizer
    ])

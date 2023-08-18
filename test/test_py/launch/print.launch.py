from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
        package="test_py",
        executable="pcl_pub",
        output="screen",
        emulate_tty=True
        )
    ])
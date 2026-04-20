from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Launch file for Stealth Infiltration sensor bridges and TF tree.

    This launch file sets up:
    1. Gazebo-ROS clock synchronization
    2. Depth camera image and info bridges
    3. Static TF tree (map -> odom -> base_link -> depth_camera_link)
    4. Depth image to laser scan conversion
    """
    return LaunchDescription([
        # Clock synchronization: Gazebo sim time -> ROS 2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='clock_bridge',
            arguments=['/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'],
        ),

        # Depth camera bridge: Gazebo -> ROS 2
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='depth_camera_bridge',
            arguments=[
                '/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
                '/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            ],
            remappings=[
                ('/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/depth_image', '/depth'),
                ('/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/camera_info', '/depth/camera_info'),
            ],
        ),

        # TF Tree: map -> odom -> base_link -> depth_camera_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_map_odom',
            arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
            parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_odom_base',
            arguments=['--frame-id', 'odom', '--child-frame-id', 'base_link'],
            parameters=[{'use_sim_time': True}],
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_base_camera',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0.5',
                '--frame-id', 'base_link', '--child-frame-id', 'depth_camera_link',
            ],
            parameters=[{'use_sim_time': True}],
        ),

        # Depth image to laser scan conversion
        Node(
            package='depthimage_to_laserscan',
            executable='depthimage_to_laserscan_node',
            name='depth_to_scan',
            parameters=[{
                'output_frame': 'depth_camera_link',
                'use_sim_time': True,
            }],
            remappings=[
                ('/depth', '/depth'),
                ('/depth_camera_info', '/depth/camera_info'),
            ],
        ),
    ])

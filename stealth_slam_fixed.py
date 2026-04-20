from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # THE FIX: Bridge Gazebo clock to ROS 2
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             arguments=['/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock']),

        # Bridge depth camera image + camera info
        Node(package='ros_gz_bridge', executable='parameter_bridge',
             arguments=[
                 '/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
                 '/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
             ],
             remappings=[
                 ('/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/depth_image', '/depth'),
                 ('/world/iris_warehouse/model/depth_camera/link/link/sensor/camera/camera_info', '/depth/camera_info'),
             ]),

        # TF tree: map -> odom -> base_link -> depth_camera_link
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
             parameters=[{'use_sim_time': True}]),
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--frame-id', 'odom', '--child-frame-id', 'base_link'],
             parameters=[{'use_sim_time': True}]),
        Node(package='tf2_ros', executable='static_transform_publisher',
             arguments=['--x', '0', '--y', '0', '--z', '0.5',
                        '--frame-id', 'base_link', '--child-frame-id', 'depth_camera_link'],
             parameters=[{'use_sim_time': True}]),

        # Convert depth image to laser scan
        Node(package='depthimage_to_laserscan', executable='depthimage_to_laserscan_node',
             parameters=[{'output_frame': 'depth_camera_link', 'use_sim_time': True}],
             remappings=[('/depth', '/depth'), ('/depth_camera_info', '/depth/camera_info')]),

        # SLAM Toolbox - THE MAP GENERATOR
        Node(package='slam_toolbox', executable='async_slam_toolbox_node',
             parameters=[{
                 'use_sim_time': True,
                 'odom_frame': 'odom',
                 'base_frame': 'base_link',
                 'scan_topic': '/scan',
             }]),
    ])

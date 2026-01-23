from setuptools import find_packages, setup
import glob
import os

package_name = 'mivia_rover_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "launch"), glob.glob("launch/*.py")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='DamoraDomenicoPio',
    maintainer_email='d.damora3@studenti.unisa.it',
    description='MIVIA Rover Perception Package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mivia_rover_perception_node = mivia_rover_perception.mivia_rover_perception_node:main',
            'perception_visualizer_node = mivia_rover_perception.perception_visualizer_node:main'
        ],
    },
)

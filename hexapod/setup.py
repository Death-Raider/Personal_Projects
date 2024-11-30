from setuptools import find_packages, setup
import os
from glob import glob
package_name = 'hexapod'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name,'urdf'), glob(package_name+'/urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob(package_name+'/meshes/*')),
    ],
    install_requires=['setuptools'],
    py_modules=['hexapod.my_node'],
    zip_safe=True,
    maintainer='darsh',
    maintainer_email='darsh@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hexapod_node = hexapod.my_node:main'
        ],
    },

)

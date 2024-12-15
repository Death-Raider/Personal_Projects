# Hexapod Movement  

## **Overview**:  
This project is a **ROS2 package** designed to visualize and simulate the movement of a hexapod robot using **rviz2**. The system incorporates realistic movement mechanisms, inverse kinematics, and efficient transformation management to mimic the behavior of a physical hexapod robot.  

---

## **Key Features**:  

1. **Visualization with rviz2**:  
   - The package uses **TF transforms** to broadcast the movement of each joint and leg dynamically.  
   - Enables real-time visualization of the hexapod's movements in rviz2.  

2. **Inverse Kinematics (IK)**:  
   - IK is implemented to calculate joint angles required for the legs to achieve the desired positions in 3D space.  
   - Ensures smooth and realistic leg movement while maintaining stability.  

3. **Realistic Leg Motion**:  
   - Feet movement mimics a walking trajectory using **parabolic equations** to define the step arc in the movement direction.  
   - Handles dynamic walking patterns with realistic motion transitions.  

4. **Rotational Algebra**:  
   - Complex rotational transformations for body orientation are managed via `rotation.py`, ensuring precise control of the hexapod's posture during movement and rotation.  

5. **Custom Datatype for Movement**:  
   - `positions.py` introduces a **custom datatype** to manage and handle movement data efficiently, simplifying calculations and data flow.  

6. **Keyboard Input for Control**:  
   - `keyboardInput.py` allows users to provide real-time movement commands, including walking direction, speed, and rotation.  

7. **Comprehensive Structure**:  
   - **Static and Dynamic Transforms**: Managed by `transformManager.py` for broadcasting both fixed and changing joint positions.  
   - **Body and Leg Classes**:  
     - `body.py` handles the hexapod's central structure and global movements.  
     - `leg.py` defines the individual legs' parameters and actions.  
   - `my_node.py` acts as the central controller, integrating all components and publishing necessary data to `/TF` for visualization in rviz2.  

---

## **Learning Outcomes**:  
- **ROS2 Framework**: Gained hands-on experience in creating ROS2 packages and broadcasting TF transforms.  
- **Mathematical Modeling**: Implemented inverse kinematics and parabolic motion for realistic hexapod leg movement.  
- **Visualization with rviz2**: Learned to create and publish real-time transforms for effective simulation.  
- **System Integration**: Combined modular components into a functional ROS2-based hexapod simulation.  

---

### **Future Enhancements**:  
- Incorporate **force sensors** for adaptive walking on uneven terrain.  
- Implement **gait patterns** for different terrains (e.g., tripod gait, wave gait).  
- Add real-time **collision detection** and avoidance using LiDAR/vision sensors.  
- Expand control input to include joystick/gamepad support.  

This project is a comprehensive exploration of ROS2-based robotics simulation, laying the groundwork for physical implementation and advanced autonomous movement in a hexapod robot.
# 6-Wheeled Rover Using ROS

This project showcases a simulated six-wheeled rover system utilizing the **Robot Operating System 2 (ROS2)** for visualization and navigation. It consists of two main components: **Terrain Navigation** and the **Rover Simulation** package.

---

## **Components**

### **1. Terrain Navigation (`Terrain_nav`)**
- **Functionality**: 
  - Generates a random **3D terrain** by superimposing multiple Gaussian surfaces.
  - Defines start and end points for navigation:  
    - **Start Point**: (0, 0)  
    - **End Point**: (100, 100)

- **Pathfinding Algorithm**:  
  - Implements the **A\*** (A-star) algorithm for finding the optimal path across the randomly generated terrain.
  - Factors in the height differences to simulate realistic terrain traversal for a six-wheeled rover.

- **Output**:  
  - A visual map of the 3D terrain with the path overlay, which can guide the rover from the start to the end point.

---

### **2. Rover Simulation (`test1`)**
This ROS2 package simulates the six-wheeled rover's movement and visualizes its transformations in **Rviz2**.  

#### **Key Files in the `test1` Package**
1. **`body.py`**  
   - Defines the physical characteristics of the rover's main body.  
   - Includes dimensions, weight distribution, and center of gravity calculations.

2. **`wheels.py`**  
   - Models the six wheels of the rover, including parameters like:  
     - Diameter  
     - Friction  
     - Torque limits  
   - Provides functionality to simulate individual wheel movements for forward and backward navigation.

3. **`transformManager.py`**  
   - Publishes **static** and **dynamic transforms** using the **TF2 framework**.  
   - Enables the visualization of transformations for each component (body, wheels) of the rover in Rviz2.

4. **`rotations.py`**  
   - Handles rotation transformations using both:  
     - **Quaternions** (for smoother and more robust 3D rotation calculations).  
     - **Euler Angles** (for simpler transformations).  
   - Includes helper functions to convert between quaternions and Euler angles.

5. **`keyboard.py`**  
   - Manages keyboard inputs for controlling the rover.  
   - Allows users to:
     - Move the rover **forward** and **backward**.  
     - Stop the rover or adjust speed as needed.

6. **`my_node.py`**  
   - Serves as the main execution file.  
   - Integrates all components (`body.py`, `wheels.py`, `transformManager.py`, `rotations.py`, and `keyboard.py`) to simulate the six-wheeled rover.
   - Publishes TF2 data for visualization in **Rviz2**, enabling users to observe:  
     - The rover's body and wheel movements.  
     - Transformations between different parts of the rover in real-time.  

---

## **Key Features**
1. **Terrain Simulation**:  
   - Randomized 3D terrain with realistic elevation and traversal challenges.  
   - A\* algorithm ensures the rover follows the most optimal path.  

2. **ROS2 Integration**:  
   - Modular code structure that leverages the ROS2 framework for simulation and visualization.  
   - Dynamic transforms enable real-time updates in Rviz2.

3. **Keyboard Control**:  
   - Users can control the rover interactively via keyboard inputs for forward and backward motion.

4. **Visualization**:  
   - Full visualization in **Rviz2** of:  
     - Rover's body and wheel positions.  
     - TF2 transformations between components.

---

## **Future Improvements**
1. **Enhanced Path Planning**:  
   - Incorporate more sophisticated algorithms like **RRT (Rapidly-exploring Random Tree)** or **D* Lite** for dynamic replanning.  
   - Account for terrain friction and slope in path cost calculations.  

2. **Obstacle Detection**:  
   - Simulate sensors (e.g., LIDAR or depth cameras) to detect and navigate around obstacles.  

3. **Physics Simulation**:  
   - Use a physics engine like **Gazebo** for more realistic wheel-terrain interaction.  

4. **Autonomous Navigation**:  
   - Implement SLAM (Simultaneous Localization and Mapping) for autonomous terrain traversal.  

5. **Additional Movements**:  
   - Include lateral movement and turning mechanics for more realistic motion.  

This project is a practical demonstration of robotics simulation, terrain navigation, and real-time visualization using ROS2, providing a solid foundation for further advancements in autonomous vehicle research.
# Google Developer Group Recruitment Competition: Heat Equation Simulation

This repository is part of a recruitment competition project that demonstrates numerical methods, data generation, and dataset analysis using a 1D heat equation. The files and their purposes are outlined below:

---

## **Repository Files**

### **1. `clean_select_DS_dept.py`**  
- **Purpose**: Filters recruitment form responses to identify candidates interested in the Data Science Department.  
- **Input**: An Excel sheet containing recruitment form responses.  
- **Output**: A filtered list of candidates tailored for the Data Science department.  

---

### **2. `test.py`**  
- **Purpose**: Exploration and numerical solution of problem statements, focusing on heat equation simulations.  
- **Features**:  
  - Tested both 1D and 2D heat equations.  
  - Final implementation focused on solving the **1D heat equation** numerically.  

- **1D Heat Equation Details**:  
  <center>
  
  ![equation](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cbg%7Bwhite%7D%5Cfrac%7B%5Cpartial%20u%7D%7B%5Cpartial%20t%7D=%5Calpha%5Cfrac%7B%5Cpartial%5E2%20u%7D%7B%5Cpartial%20x%5E2%7D) 
  </center>
  
  where:
  - \( u(x, t) \) is the temperature distribution along the rod.  
  - \( α = 0.14159 \) is the thermal diffusivity constant.  

- **Initial Condition**:  
  A sinusoidal temperature distribution along the rod.  

- **Rod Lengths**: Simulated for varying lengths from **0.2 to 1.2 units**.  

- **Spatial Discretization**:  
  - \( nx = 50 \) sensors (data points) distributed evenly along the rod.  

- **Output**:  
  A dataset of temperature profiles over time for rods of different lengths.  

---

### **3. `usedataset.py`**  
- **Purpose**: Demonstrates how to load and preprocess the generated dataset.  
- **Dataset Format**:  
  - Each file contains 100 test cases (trials).  
  - Each row corresponds to a snapshot of the temperature profile along the rod.  

---

## **Dataset Details**

### **Structure**  
- **Columns**:  
  - `ID`: Unique identifier for each data point.  
  - `L`: Length of the rod (in arbitrary units).  
  - `nx`: Number of sensors (fixed at 50).  
  - `val_0` to `val_nx-1`: Temperature values at each sensor point (from leftmost to rightmost).  

- **Time Series Representation**:  
  - Consecutive rows represent temperature profiles at successive time steps.  

---

## **Key Features of the Dataset**  

1. **Multiple Files**:  
   - The dataset is split into **Train** and **Validation** sets.  
   - Each set contains multiple files, each simulating 100 test cases to mimic real-world experimental trials.  

2. **Synthetic Noise**:  
   - Introduced noise in both the Train and Validation datasets to simulate measurement errors.  

3. **Dataset Shift**:  
   - Before merging files, a dataset shift analysis is recommended to ensure consistency and mitigate biases.  

---

## **Applications**

- **Numerical Simulation**: Provides a platform to study heat conduction in 1D rods.  
- **Time Series Analysis**: Useful for analyzing temperature evolution over time.  
- **Machine Learning**: Can be used to train models for predictive maintenance or anomaly detection in thermal systems.  

---

## **Limitations and Future Work**

### **Limitations**  
1. Noise affects dataset precision, though this is intentional for realism.  
2. Only the 1D heat equation is fully implemented; extending this to 2D/3D equations could enhance the dataset.  
3. Dataset size may become a bottleneck for memory-constrained systems.

### **Future Enhancements**  
1. **2D/3D Heat Equation**: Extend simulations to higher dimensions for more complex systems.  
2. **Additional Features**: Include boundary conditions, material properties, or external heat sources.  
3. **Visualization**: Create interactive visualizations for better understanding of heat diffusion.  
4. **Customizable Parameters**: Allow users to input their own values for \( α, nx, \) and other parameters.  

This project effectively demonstrates the ability to solve numerical problems and generate structured datasets, showcasing analytical skills and programming expertise!
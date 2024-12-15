# Complex Matrix Visualization (SoME 1, 2 by 3B1B)

## Project Overview

This project visualizes **2x2 complex matrices** and explores their properties in 3D and 4D spaces. By leveraging **Pauli matrices**, the project demonstrates how complex matrices can represent rotations in 3D space and manipulate vectors and planes. Inspired by **3Blue1Brown's Essence of Linear Algebra series**, the project is divided into two parts:

### **3B1B-1: 3D Complex Matrix Visualization**
1. **Rotation in 3D Space**:
   - Visualizes how 2x2 complex matrices transform vectors and planes in 3D using **Pauli matrices**.
   - Demonstrates vector rotation using **color as a visual cue**.

2. **Color Shifting**:
   - Represents the rotation of 3D vectors about another color vector through `color_shifter.py`.
   - Displays the concept of domain coloring (`domainC.py`) to show the complex plane under rotation, using colors to indicate the phase of transformation.

### **3B1B-2: 4D Complex Matrix Visualization**
1. **Rotation in 4D Space**:
   - Visualizes how 4D points are rotated using complex matrices.
   - Projects these rotations onto a torus using **Hopf projection**.
   - Demonstrates the effect of rotations on 4D planes through animations.

---

## Key Features

### **3B1B-1**
- **Color Shifter**:
  - Script: `color_shift.py`
  - Animation: `color_shift.mp4`
  - Visualizes rotations in 3D vectors using color as an axis of rotation.
  
- **Domain Coloring**:
  - Script: `domainC.py`
  - Visualizes how the complex plane is transformed under rotation, with color indicating the phase of the transformation.

- **3D Transformations**:
  - Animations in `anim/` folder (`linear_trans.mp4`, `rot3D.mp4`, `scale.mp4`, `shear.mp4`) showcase various 3D transformations, including rotation, scaling, and shearing.

### **3B1B-2**
- **Hopf Projection**:
  - Projects the rotation of 4D points onto a torus.
  - Visualizes 4D transformations using animations (`animation@10.mp4`).

- **4D Transformations**:
  - Rotations of 4D planes visualized through `plane.py` and `rotation.py`.

---

## Project Structure

```plaintext
Complex-Matrix-Visualization/
├── 3b1b1/                       # Visualizations for 3D Complex Matrices
│   ├── JS/
│   │   ├── matrix_visual.js     # JavaScript script for 3D matrix visualization
│   │   ├── package-lock.json    # Dependencies for JavaScript files
│   ├── PY/
│   │   ├── anim/                # Animation files for transformations
│   │   │   ├── linear_trans.mp4
│   │   │   ├── rot3D.mp4
│   │   │   ├── scale.mp4
│   │   │   ├── shear.mp4
│   │   ├── color_shift_rotation/
│   │   │   ├── color_shift.py   # Script for color shifting rotation
│   │   │   ├── color_shift.mp4  # Animation for color shifting
│   │   │   ├── color.jpg        # Color image for rotation visualization
│   │   ├── domainC.py           # Domain coloring script
│   │   ├── make_anim.py         # Script for creating animations
│   │   ├── rotation_pauli.py    # Rotation using Pauli matrices
├── 3b1b2/                       # Visualizations for 4D Complex Matrices
│   ├── plane.py                 # 4D plane rotation
│   ├── rotation.py              # Rotation in 4D
│   ├── animation@10.mp4         # Animation for 4D transformations
│   ├── utils.py                 # Utility functions
├── .gitignore                   # Git ignore file
├── README.md                    # Project documentation
```

---

## Prerequisites

1. **Software Requirements**:
   - Python 3.8 or above
   - Libraries: `numpy`, `matplotlib`, `manim`, `scipy`, `pillow`
   - JavaScript runtime (e.g., Node.js for `matrix_visual.js`).

2. **Hardware Requirements**:
   - GPU (optional) for faster rendering of animations.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Summer-of-Math-Exposition-Projects-(3B1B)
   ```

2. Set up JavaScript dependencies (if using `matrix_visual.js`):
   ```bash
   cd 3b1b1/JS
   npm install
   ```

---

## Usage

### 1. Visualize 3D Complex Matrices (3B1B-1)
- **Color Shifting**:
  Run the `color_shift.py` script to generate animations:
  ```bash
  python 3b1b1/PY/color_shift_rotation/color_shift.py
  ```
  The output animation (`color_shift.mp4`) will be saved in the same directory.

- **Domain Coloring**:
  Visualize domain coloring with the following command:
  ```bash
  python 3b1b1/PY/domainC.py
  ```

- **3D Transformations**:
  Generate animations for linear transformations (rotation, scaling, etc.):
  ```bash
  python 3b1b1/PY/make_anim.py
  ```
  Animations are saved in the `anim/` folder.

### 2. Visualize 4D Complex Matrices (3B1B-2)
- **Hopf Projection**:
  Run `plane.py` or `rotation.py` to visualize 4D rotations:
  ```bash
  python 3b1b2/plane.py
  python 3b1b2/rotation.py
  ```
  Output animations are saved as `animation@10.mp4`.

---

## Future Enhancements

1. **Higher-Dimensional Projections**:
   - Extend to 5D or higher-dimensional projections.
   - Explore advanced visualization techniques for higher-dimensional data.

2. **Interactive Visualizations**:
   - Build a web-based interactive visualization tool for complex matrices.

3. **Integration with 3Blue1Brown Manim Library**:
   - Enhance visualizations using 3Blue1Brown's **Manim** library for better aesthetics.

---

## Acknowledgments

- **3Blue1Brown**: Inspiration from the "Essence of Linear Algebra" series.
- **Manim**: A mathematical animation engine for creating visualizations.
- **Hopf Projection**: Theoretical foundation for projecting 4D rotations onto a torus.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
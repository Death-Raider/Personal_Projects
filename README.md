# Projectile Motion Website with P5.js  

## Overview 🌟  
This project showcases a **basic physics simulation** using **P5.js**, where users can interactively plot the trajectory of a projectile (box). It was created as an introduction to the P5.js module for physics-based visualizations and simulations.  

The project allows users to:  
1. Drag and place a box with their mouse.  
2. Simulate and visualize the projectile motion trajectory when the box is "thrown."  

---

## Basic Functionality 🚀  

The core logic involves physics concepts such as gravity and motion.  

### Key Code Snippets  

```javascript  
let box;  
let time = 0;  

function setup() {  
  let canvas = createCanvas(1510, 400);  
  box = new Box(20, 20, 20, 20);  
  box.reset();  
  background(51);  
}  

function mouseDragged() {  
  rectMode(CENTER);  
  box.teleport(mouseX, mouseY);  
  time = 0;  
  box.reset();  
  background(51);  
}  

function draw() {  
  rectMode(CENTER);  
  rect(width / 2, height, width, 20);  
  box.show();  
  if (box.y + box.h < height) {  
    box.fall(time);  
    time += 0.1;  
  } else {  
    box.y = height - box.h;  
    time = 0;  
  }  
}  
```  

---

## Features 🧩  

### Current Features:  
- **Interactive Mouse Dragging:** Users can summon the box at any position using a mouse drag.  
- **Physics-Based Projectile Motion:** Once placed, the box follows a realistic trajectory under the influence of gravity.  

---

### Future Improvements: 🌟  
1. **Enhanced Object Complexity:**  
   - Introduce objects of varying shapes and sizes (e.g., circles, triangles, etc.).  
2. **Multiple Objects:**  
   - Add support for simultaneous projectile motion of multiple objects.  
3. **Gamification & Customization:**  
   - Allow users to design and customize the environment (e.g., obstacles, platforms).  
   - Gamify the experience by introducing objectives or challenges (e.g., hit a target).  

---

## How to Run the Project 💻  

### Steps:  
1. Clone or download this repository.  
2. Open the `index.html` file in a browser 
3. Drag your mouse on the canvas to summon and simulate the projectile motion of the box.  

---

## Project Structure 📂  

```
/Projectile-Motion  
├── README.md           # Read me for the project  
├── index.html           # Entry point of the website  
├── index.js            # Contains the P5.js code  
├── box.js               # Class definition for the Box object  
└── main.css            # Styling for the canvas and website  
```  

---

## Key Learnings & Motivation 💡  

- Understanding **P5.js** as a framework for visual and interactive simulations.  
- Applying **physics concepts** such as gravity, velocity, and motion in a visual format.  
- Exploring user interaction with a **dynamic physics-based system**.  

---

## License 📜  

This project is licensed under the **MIT License**, so feel free to use it and modify it as needed.  
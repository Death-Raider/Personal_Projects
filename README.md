# Handwritten Digit Dataset Collection and Modeling

## Project Overview

This project was designed to provide a hands-on understanding of several critical components in modern software and machine learning development, including:

1. **Data Collection**:
   - Building a front-end web application for users to draw and label handwritten digits.
   - Server-side validation and storage of data using **MongoDB**.

2. **Data Augmentation and Modeling**:
   - Training a neural network using custom and collected handwritten digit data.
   - Using the **[@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network)** library to train and test the model.

3. **Full-Stack Development**:
   - **Front-End**: HTML, CSS, and JavaScript to design an interactive user interface.
   - **Back-End**: Node.js and Python for server logic and neural network processing.
   - **Database**: MongoDB for efficient data storage and retrieval.

---

## Project Structure

The project is divided into two major components:

### **1. Data Collection**
- A user-friendly website was developed to allow users to draw and label handwritten digits.
- **Features**:
  - Users can draw a digit on a canvas and assign a label.
  - Real-time validation by the server ensures:
    - The drawn digit resembles a number through **meta classification**.
    - The number of activated pixels (set values) in the drawing lies within an acceptable range.
  - Validated data is stored in a **MongoDB cluster** for further use.

- **Technologies Used**:
  - **Front-End**:
    - HTML/CSS: For designing an interactive UI.
    - JavaScript: For canvas drawing functionality.
  - **Back-End**:
    - Node.js: For handling requests and server-side validation.
  - **Database**:
    - MongoDB: For storing the collected digit data.

---

### **2. Data Prediction**
- The collected data was used to train a neural network for handwritten digit recognition.
- **Training**:
  - A neural network was trained using the **[@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network)** library.
  - The model was tested and evaluated using the collected dataset.

- **Technologies Used**:
  - **Back-End**:
    - Python: For pre-processing and exporting data to the training pipeline.
    - Node.js: To integrate the trained model into the backend for predictions.
  - **Neural Network Library**:
    - Custom library: [@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network) was used for training and inference.

---

## Execution Workflow

1. **Data Collection**:
   - Open the web application.
   - Draw a digit on the canvas and assign it a label.
   - The server validates the input:
     - Compares the input with existing data for consistency using **meta classification**.
     - Checks if the active pixel count of the drawn image falls within a predefined range.
   - Once validated, the labeled digit is saved in the **MongoDB cluster**.

2. **Data Prediction**:
   - The labeled data stored in the database is exported and augmented for training.
   - A neural network is trained using the **[@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network)** library.
   - The trained model is deployed on the backend to provide predictions for new inputs.

---

## Key Features

- **Interactive Front-End**:
  - Allows users to draw, label, and submit handwritten digits.
  - Canvas provides an intuitive interface for data collection.

- **Real-Time Validation**:
  - Ensures that submitted drawings are valid representations of digits before storing them.
  - Enhances data quality and reduces noise in the dataset.

- **Custom Neural Network**:
  - Built and trained using the **[@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network)** library.
  - Designed for efficient handwritten digit recognition.

- **Full-Stack Integration**:
  - Combines front-end, back-end, and database services seamlessly.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Handwritten-Digit-Dataset-Collection-and-Modeling
   ```

2.
# MED x AI

## Project Overview

**MED x AI** is a comprehensive project that combines artificial intelligence with healthcare to predict fractures in X-ray scans. The project includes the development of a **YOLOv8m-based fracture prediction model** and a **chatbot** capable of interacting with users to answer queries and support multimedia inputs such as PDFs, audio, and images. The web application serves as an interface to showcase the prediction model and the chatbot.

---

## Key Features

1. **Fracture Prediction**:
   - A **YOLOv8m** model is used for accurate fracture detection in X-ray scans. 
   - Trained on a curated dataset, the model predicts fractures with bounding boxes and confidence scores.

2. **Interactive Chatbot**:
   - Built using the **Llama model** and **LLM chains**, the chatbot supports:
     - Text-based queries.
     - Analysis of **PDFs**, **audio files**, and **images** for enhanced user assistance.
     - Contextual understanding through **chat history**.

3. **Web Application**:
   - A user-friendly interface to showcase the fracture prediction model and the chatbot.
   - Upload X-ray scans for fracture analysis.
   - Interact with the chatbot for queries related to fractures, X-ray imaging, and dataset usage.

---

## Dataset

The following datasets were used to train and evaluate the fracture prediction model:

1. **Main Dataset**:
   - Source: [Bone Fracture Detection](https://www.kaggle.com/datasets/pkdarabi/bone-fracture-detection-computer-vision-project)
   - Description: A large dataset containing X-ray scans labeled with fracture annotations.

2. **Supplementary Dataset**:
   - Source: [Promising Bone Break Dataset](https://www.kaggle.com/datasets/pkdarabi/bone-break-classification-image-dataset)
   - Description: A smaller dataset for bone break classification, used to enhance model accuracy.

3. **Existing Models and References**:
   - [Russian Documentation Bone Break Dataset](https://www.kaggle.com/code/antongalysh/image-classification): Used for comparative analysis.
   - [YOLOv8 Low Accuracy Model](https://www.kaggle.com/code/jasonroggy/yolov8): Provided insights into improvements needed for model training and optimization.

---

## Technologies Used

1. **Model**:
   - **YOLOv8m**: Selected for its balance between speed and accuracy for object detection tasks.

2. **Chatbot**:
   - **Llama Model**: Lightweight and efficient language model for conversational AI.
   - **LLM Chains**: Used for building advanced chatbot workflows.

3. **Web Application**:
   - Built using frameworks like **Flask** or **FastAPI** for backend integration.
   - Frontend developed with **HTML**, **CSS**, and **JavaScript** for seamless user interaction.

4. **Data Handling**:
   - **Kaggle Datasets** for training and evaluation.
   - **Multimedia Processing** for PDFs, audio, and images in the chatbot.

---


## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd MedXAI_Internship_Project-Bone-Fracture
   ```
---

## Usage

### Web Application
Start the web application for an integrated user experience:
```bash
node Webapp/server.js
```
- Access the app in your browser (e.g., `http://127.0.0.1:3000`).
- Upload X-ray scans for predictions or interact with the chatbot.

---

## Future Enhancements

1. **Model Improvements**:
   - Fine-tune YOLOv8m with additional labeled data for improved performance.
   - Explore ensemble methods for fracture prediction.

2. **Chatbot Enhancements**:
   - Integrate more robust LLMs for deeper medical knowledge.
   - Add multilingual support for wider accessibility.

3. **Web Application**:
   - Build a dashboard to display prediction statistics and history.
   - Add secure login functionality for personalized user experiences.

---

## Acknowledgments

- **Kaggle Datasets**: For providing high-quality datasets for training and evaluation.
- **Llama Model**: For powering the chatbot functionality.
- **YOLOv8**: For enabling state-of-the-art object detection capabilities.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
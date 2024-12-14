# Rainfall Prediction for Agriculture

## Project Overview

This project leverages rainfall data provided by **CCS India** to analyze and predict rainfall patterns across the Indian peninsula. The goal is to enable better agricultural planning and decision-making by visualizing rainfall distribution, creating an animation of historical data, and building a Convolutional Neural Network (CNN) model for prediction. 

Additionally, the project includes an interactive chatbot powered by **GPT4All**, enabling users to address queries and gain insights related to the project.


## Key Features

1. **Rainfall Data Processing**:
   - Utilizes rainfall data from **2018 to 2022**, stored in `nc` file format.
   - Processes and visualizes rainfall data for each day across multiple years.

2. **Visualization**:
   - A folder named `images` contains a base map of India for plotting rainfall distributions.
   - A pre-generated **MP4 animation** provides a dynamic visualization of rainfall trends over time.

3. **Machine Learning**:
   - A **CNN model** is trained on rainfall data to predict future patterns, aiding agricultural planning.

4. **Interactive Chatbot**:
   - A script (`GPT4all_chatbot.py`) implements a **GPT4All-based chatbot** to answer user queries and provide insights about the project.

---

## Project Structure

```plaintext
Rainfall-Prediction/
├── data/
│   ├── 2018.nc         # Rainfall data for the year 2018
│   ├── 2019.nc         # Rainfall data for the year 2019
│   ├── 2020.nc         # Rainfall data for the year 2020
│   ├── 2021.nc         # Rainfall data for the year 2021
│   ├── 2022.nc         # Rainfall data for the year 2022
├── images/
│   ├── india.png         # Base map of India for plotting rainfall
│   ├── Resized.png       # Base map of India for plotting rainfall
│   ├── india_output.png  # Base map of India for plotting rainfall
├── animations/
│   ├── animation@10.mp4  # Animation showcasing rainfall trends
├── parse_data.py       # Script for handling netCDF4 files and extracting rainfall data
├── train.py            # Script for training the CNN model
├── GPT4all_chatbot.py  # GPT4All-based chatbot for interactive queries
└── README.md               # Project documentation
```

---

## Prerequisites

1. **Software Requirements**:
   - Python 3.8 or above
   - Libraries: `numpy`, `pillow`, `tensorflow`, `netCDF4`, `opencv-python`, `gpt4all`
   - GPU (recommended) for training the CNN model.

2. **Data**:
   - The project includes `nc` files containing rainfall data for the years 2018–2022.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Rainfall-Prediction
   ```

2. Ensure the `data/` folder contains all five `.nc` files:
   - `2018.nc`, `2019.nc`, `2020.nc`, `2021.nc`, and `2022.nc`.

---

## Usage

### 1. **Data Parsing**
The `parse_data.py` script processes the rainfall data stored in `.nc` files:
- Extracts daily rainfall data.
- Generates plots for rainfall visualization on the base map of India.

### 2. **Visualization**
Generated rainfall plots are saved in the `images/plots/` directory. To view the rainfall trends dynamically:
```bash
open animations/rainfall_animation.mp4
```

### 3. **Model Training**
The `train.py` script trains a CNN model using the processed rainfall data:
```bash
python train.py
```
- Outputs a trained model saved in the `models/cnn_model.h5` file.
- Model performance metrics are displayed during the training process.

### 4. **Interactive Chatbot**
Run the **GPT4All chatbot** to interact and get insights about the project:
```bash
python GPT4all_chatbot.py
```

### Example Queries for the Chatbot:
- "How is rainfall pattern prediction important for agriculture?"
- "How can farmers do to predict rainfall?"

---

## Future Enhancements

1. **Model Improvements**:
   - Enhance the CNN model with additional meteorological data (e.g., temperature, humidity).
   - Experiment with advanced deep learning architectures for better accuracy.

2. **Data Expansion**:
   - Incorporate more historical rainfall data or real-time rainfall data feeds.

3. **Automation**:
   - Automate daily rainfall predictions and visualizations for real-time agricultural use.

4. **Interactive Dashboard**:
   - Develop a web-based dashboard for visualizing rainfall data, predictions, and insights interactively.

---

## Acknowledgments

- **CCS India** for providing the rainfall data.
- **GPT4All Library** for enabling a lightweight and efficient chatbot solution.
- **netCDF4** for efficient handling of large-scale meteorological data.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
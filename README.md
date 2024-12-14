# Minecraft Agent

## Project Overview

The **Minecraft Agent** is designed to interact autonomously within the Minecraft environment. It is equipped with movement capabilities, a bounding box detection system for identifying mobs, and terrain segmentation for understanding the surrounding environment. The project combines computer vision techniques with reinforcement learning principles to enable agents to navigate and make decisions in the Minecraft world.

### Key Features
- **Movement and Interaction**: 
  - The agent has autonomous movement functionality.
  - Currently, movement is implemented using static states, with plans to integrate dynamic autonomous behavior.
  
- **Dual Vision System**: 
  - A **bounding box detection system** is used to detect and locate mobs (Minecraft entities).
  - A **segmentation system** is used to analyze and label surrounding terrain, aiding navigation and decision-making.

- **Datasets**:
  - **Bounding Box Detection**: Dataset is available on Roboflow: [Minecraft-Mob](https://app.roboflow.com/oragimirox-gmail-com/minecraft-mob/6).
  - **Segmentation**: The segmentation dataset has been curated and is readily available within the project resources.

---

## Technologies Used

1. **Bounding Box Detection**:
   - The project leverages **YOLOv5** (You Only Look Once, Version 5) for efficient and real-time bounding box detection of mobs in gameplay images.

2. **Segmentation**:
   - A **U-Net architecture** is employed for terrain segmentation, facilitating accurate pixel-wise classification of the Minecraft environment.

3. **Image Processing**:
   - Custom tools and scripts are used for Minecraft gameplay image labeling and dataset creation.

---

## Project Structure

```plaintext
Minecraft-Segmentation/
├── U-NET_SEG/
│   ├── Annoted_images/  
│   ├── labels/
│   ├── mob_dataset/     
│   │   ├── __init.py__
│   │   ├── mob_dataset.py
│   ├── annoted_remove.py
│   ├── create_dataset.py
│   ├── labelme_helper.py
│   ├── my_model.py
│   ├── utils.py
│   ├── model.png
├── YOLO5_BBX/
│   ├── Images_resize/  
│   ├── Images_resize_new/
│   ├── Output/
|   │   ├── exp/
|   │   │   ├── compressed-result.mp4
|   │   │   ├── result.avi
│   ├── parse.py
│   ├── use.py
├── movement.py
├── results.py
├── testing.avi
└── requirements.txt
```

---

## Setup and Installation

### Prerequisites
- Python 3.8 or above
- NVIDIA GPU with CUDA support (recommended for training and inference)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Minecraft-Agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download datasets:
   - Bounding Box Detection: [Download Here](https://app.roboflow.com/oragimirox-gmail-com/minecraft-mob/6)
   - Place the datasets in the `datasets/` directory.

4. (Optional) Configure your environment for GPU acceleration if using YOLOv5 or U-Net.

---

## Future Work
- **Dynamic Movement**: Transition from static state movement to a fully autonomous reinforcement learning model for decision-making.
- **Enhanced Dataset**: Expand the segmentation and bounding box datasets for better model generalization.
- **Integration**: Combine bounding box detection and terrain segmentation for end-to-end autonomous behavior in the Minecraft world.

---

## Acknowledgments
- YOLOv5: [Ultralytics](https://github.com/ultralytics/yolov5)
- U-Net: [Original Paper](https://arxiv.org/abs/1505.04597)
- Dataset hosted on Roboflow: [Minecraft-Mob](https://app.roboflow.com/oragimirox-gmail-com/minecraft-mob/6)

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
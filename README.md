# Food Calorie Estimation using Vision Transformer and Custom DNN Architecture  

### By: Darsh Kachroo 
### Dataset: [IEEE FooDD](https://www.kaggle.com/datasets/darsh22blc1378/foodd-ieee-datasets)
### Code: [Kaggle Link](https://www.kaggle.com/code/darsh22blc1378/calorie-prediction-using-vision-transformers)

---

## **Objective**  
The project aimed to create a deep learning-based system to estimate the calorie count of food items from images. Two primary approaches were explored: **Vision Transformer (ViT)** and a **Custom Deep Neural Network (DNN)** with modular blocks designed for efficient feature extraction and processing.  

---

## **Architectural Components**  

### 1. **Vision Transformer (ViT)**:  
ViT was employed to leverage its patch-based attention mechanism for feature extraction. Key features include:  
- Input images divided into **patches** of a specified size.  
- Patches converted into embeddings using a **projection dimension**.  
- Features processed by a **transformer encoder** with multiple layers and attention heads.  
- A Multi-Layer Perceptron (MLP) head used for final calorie estimation.  

### 2. **Custom Deep Neural Network (DNN)**:  
The DNN architecture used a modular approach for feature processing:  

#### **Feature Extraction Block (FEB)**  
- Extracts low-level features from input images.  
- Includes `n` convolutional layers with **1x1 convolutions** for shape preservation.  

#### **Feature Localization Block (FLB)**  
- Focuses on critical regions of the feature maps.  
- Uses pooling and upsampling for spatial localization without altering shape.  

#### **Feature Reduction Block (FRB)**  
- Reduces the dimensionality of feature maps using pooling layers.  
- Acts as the encoder part of an autoencoder by compressing input into a latent space.  

#### **Feature Distillation Block (FDB)**  
- Produces a compact, informative representation of features.  
- Avoids padding in convolutions and excludes skip connections for simplicity.  

---

## **Hyperparameter Optimization**  

### **Vision Transformer (ViT)**  
Hyperparameters tuned using **Hyperband Optimizer**:  
- **Patch size**: 50  
- **Projection dimension**: 32  
- **Transformer layers**: 5  
- **Attention heads**: 8  
- **MLP head units**: 660, 56  
- **Transformer units**: 112  

### **Custom DNN**  
The architecture was tuned for optimal performance using the **Hyperband Optimizer**, which adjusted:  
- Number of blocks, filter size, and dropout rate.  
- Block combinations for pooling, convolutional reduction, and localization.  
- Reduction block depth and configuration for each block.  

#### Final Hyperparameters:  
- **Model length**: 3  
- **Dropout rate**: 0.2  
- **Filters**: 56  
- Block configurations: Various combinations of pooling, convolution, and localization for flexibility.  

---

## **Results**  

| Metric          | Vision Transformer | Custom DNN |  
|------------------|--------------------|------------|  
| **Training Loss** | 242.02             | 25.02       |  
| **Training MAE**  | 11.37              | 3.51        |  
| **Validation Loss** | 19.33             | 26.4        |  
| **Validation MAE**  | 2.43              | 3.41        |  
| **Test Loss**     | 22.87              | 30.2        |  
| **Test MAE**      | 2.70               | 3.76        |  

### **Key Observations**  
- ViT demonstrated superior **extrapolation capabilities** for unseen data.  
- The DNN showed competitive performance with significantly lower training loss, suggesting strong learning on the training set.  

---

## **Takeaways**  
1. **ViT Strengths**:  
   - Better at generalizing to unseen data due to its attention mechanism.  
   - Capable of capturing complex spatial dependencies in images.  

2. **Custom DNN Strengths**:  
   - Modular architecture allowed fine control over feature extraction, localization, and reduction.  
   - Simpler and faster to train compared to ViT.  

---

## **Future Work**  
1. Integrate **data augmentation** for better generalization.  
2. Implement **ensemble methods** combining ViT and DNN predictions for improved accuracy.  
3. Explore **pretrained ViT models** for better feature extraction.  
4. Incorporate **multi-task learning** to estimate multiple food properties (e.g., weight, ingredients).  

This project demonstrates how advanced architectures like Vision Transformers and modular custom DNNs can be utilized effectively for calorie estimation, offering insights into practical model design and optimization.  
# GDSC 2023 Recruitment Assignment - Kaggle Competition  

## **Overview**:  
This project involves creating and optimizing machine learning models to tackle a classification problem for GDSC's Kaggle-style recruitment assignment. The dataset consists of **train**, **test**, and **sample submission** files. The primary goal was to identify the best-performing model and generate predictions for submission.  

---

## **Dataset**:  

The dataset is located in the `Dataset` folder, consisting of:  
- `train.csv`: Training data for model development.  
- `Kaggle_test.csv`: Test data for evaluation and submission.  
- `Sample_Submission.csv`: Sample format for submission file.  

---

## **Approach**:  

### **Feature Engineering**:  
1. **Correlation Analysis**:  
   - Correlation between features was analyzed to identify the best predictors.  
   - Irrelevant or highly correlated features were dropped to reduce dimensionality and improve model performance.  

2. **Feature Scaling**:  
   - Standardized features to ensure compatibility with algorithms sensitive to scaling.  

---

### **Model Development**:  

Multiple models were implemented, each fine-tuned to maximize performance:  

1. **Random Forest Classifier**:  
   - Employed **RandomizedSearchCV** for hyperparameter tuning.  
   - Tuned parameters included the number of estimators, max depth, and minimum samples split.  

2. **Support Vector Classifier (SVC)**:  
   - Explored both linear and non-linear kernels.  
   - Optimized `C` and `gamma` parameters for the RBF kernel.  

3. **Gradient Boosting Classifier (GBC)**:  
   - Tuned hyperparameters such as the learning rate, number of estimators, and max depth.  

4. **Fully Connected Dense Neural Network**:  
   - Built using a combination of **Categorical Cross-Entropy (CCE)** and **Sparse Categorical Cross-Entropy (SCCE)** as loss functions.  
   - Employed **Bayesian Optimization** for hyperparameter tuning, focusing on:  
     - Number of hidden layers  
     - Neurons per layer  
     - Learning rate  
     - Dropout rate  

---

### **Model Selection**:  
- The **best model** was selected based on its performance metrics (e.g., accuracy, precision, recall, and F1-score) evaluated on a validation set.  
- The selected model was applied to `Kaggle_test.csv` for generating predictions.  

---

## **Submission**:  
The predictions from the best-performing model were saved in `submission.csv`, adhering to the format provided in `Sample_Submission.csv`.  

---

## **Learning Outcomes**:  
- **Feature Engineering**: Learned to use correlation analysis to enhance model performance.  
- **Model Tuning**: Explored different optimization techniques such as Randomized Search and Bayesian Optimization for hyperparameter tuning.  
- **Model Evaluation**: Practiced evaluating and comparing different classification algorithms.  
- **End-to-End Workflow**: Gained experience in the full machine learning pipeline, from feature selection to submission.  

---

### **Future Enhancements**:  
- Implement **ensemble learning** techniques to combine predictions from multiple models for improved accuracy.  
- Explore additional feature engineering techniques like PCA or feature importance-based selection.  
- Include more robust evaluation metrics (e.g., AUC-ROC) for better model comparison.  

This project was a comprehensive exercise in building and optimizing classification models while adhering to a Kaggle competition's workflow. 

### **Results**:
- Achieved top 15 out of 55 participants in the competetion
- Selected into GDSC after interview round
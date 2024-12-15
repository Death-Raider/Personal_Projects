# IBM HR Analytics - Attrition Prediction

This project involves predicting employee attrition in an organization using machine learning techniques. The dataset used is **WA_Fn-UseC_-HR-Employee-Attrition.csv**, and various tools like Python (with libraries for data analysis and visualization) and Tableau were utilized for exploration and analysis.

---

## Project Files Overview

1. **analysis.py**  
   A Python script that loads the dataset and performs data analysis, followed by generating popup graph windows for visualizing the findings.

2. **analysis.ipynb**  
   A Jupyter notebook that showcases the complete analysis workflow, providing outputs, visualizations, and step-by-step commentary.

3. **IBM_HR_Analytics.twb**  
   Tableau Workbook file used for building the interactive Tableau dashboard.

4. **IBM_HR_Analytics.png**  
   Image of the Tableau dashboard created using the data, which visually represents key insights regarding employee attrition.

---

## Dataset

- **File**: `WA_Fn-UseC_-HR-Employee-Attrition.csv`  
- **Kaggle link**: [Attrition Prediction - Complete Comparative Study](https://www.kaggle.com/code/darsh22blc1378/attrition-prediction-complete-comparitive-study)

This dataset includes multiple employee attributes such as:
- Age
- Department
- Job Role
- Marital Status
- Number of years in the company
- And more...

The goal is to predict whether an employee will leave the organization (attrition).

---

## Getting Started

### 1. Setup

Before running the analysis files, ensure all required dependencies are installed by running:

```bash
pip install -r requirements.txt
```

This will install all the necessary libraries such as `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, and others.

### 2. Running the Analysis

- **analysis.py**  
  Run the `analysis.py` file, and it will perform the analysis and show popup windows with graphs that visualize the key insights from the dataset.

```bash
python analysis.py
```

- **analysis.ipynb**  
  Open `analysis.ipynb` in Jupyter Notebook or JupyterLab, and run the cells to perform the analysis interactively. Each output, along with graphs and visualizations, will be shown directly within the notebook.

---

## Tableau Analysis Dashboard

A comprehensive Tableau dashboard has been created to visualize the data and insights. The dashboard includes:
- Attrition rates across different departments and job roles.
- Correlations between various factors (e.g., age, job satisfaction, years at company) and employee attrition.
- Predictive analytics for identifying employees who are at high risk of attrition.

### Screenshot of the Dashboard

![IBM HR analytics](IBM_HR_Analytics.png)

---

## Conclusion

This project combines data analysis, machine learning, and data visualization to identify key factors contributing to employee attrition. By using both Python and Tableau, the analysis can be explored in depth, providing actionable insights for human resources management.

# Mathematical Modeling for Stock Prediction  

## Overview  

This project explores the use of **Taylor Series** for predicting stock values, integrating mathematical modeling with real-time market data and automated trading. By leveraging APIs and automation libraries, it demonstrates how mathematical tools can be applied to stock prediction and trading.

---

## Features  

1. **Taylor Series Approximation**  
   - Uses mathematical modeling to predict the future value of stocks based on Taylor Series.  
   - Focuses on small time increments for accurate approximations.  

2. **Real-Time Stock Data**  
   - Integrates **Alphavantage API** to fetch current stock values and historical data for analysis.  

3. **Automated Trading**  
   - Implements trading automation via **Autopy**, enabling the program to control mouse actions for executing trades on trading platforms.  

4. **JavaScript-Python Integration**  
   - **stonks.js** interacts with **stonks2.py** through child processes, combining the strengths of both languages for seamless execution.  

---

## File Structure  

```
Stock-Prediction/  
├── stonks.js                  # Main JavaScript file handling API calls and Taylor Series computation
├── stonks2.py                 # Python script for trade execution
└── README.md                  # Documentation
```  

---

## How It Works  

1. **Stock Data Retrieval**  
   - `stonks.js` fetches real-time stock data from **Alphavantage API** and sends it to `stonks2.py` via child processes.  

2. **Prediction Using Taylor Series**  
   - The Python script processes the data and predicts the next value using Taylor Series approximation.  
   - Predictions are fed back to `stonks.js` for display or trade execution.  

3. **Trade Execution**  
   - If the predicted value meets certain conditions (e.g., above or below thresholds), `stonks2.py` triggers **Autopy** to execute trades automatically.  

---

## Installation  

### Prerequisites  

1. Node.js  
2. Python 3.8 or above  
3. Alphavantage API key  

### Steps  
1. Install Node.js dependencies:  
   ```bash  
   npm install  
   ```  

2. Add your Alphavantage API key in `stonks.js`:  
   ```javascript  
   const API_KEY = 'your-alphavantage-api-key';  
   ```  

---

## Running the Project  

1. Start the JavaScript script:  
   ```bash  
   node stonks.js  
   ```  

2. The JavaScript script will call `stonks2.py` to execute trades.  

---


## Libraries Used  

1. **Python**  
   - `requests`: For API integration.  
   - `autopy`: For mouse control and automated trading.  
   - `numpy`: For mathematical computations.  

2. **JavaScript**  
   - `child_process`: For communication with Python scripts.  
   - `axios`: For API requests.  

---

## Future Improvements  

1. Implement a more robust mathematical model for long-term predictions.  
2. Introduce ML models to complement Taylor Series predictions.  
3. Add error handling for API requests and automated trades.  
4. Build a web-based dashboard for better visualization of stock trends and trade logs.  

---

## Disclaimer  

This project is for educational purposes only. **Trading involves financial risk**, and the use of this project in live markets should be done cautiously. Always consult with a financial expert before making investment decisions.  

---  

Feel free to contribute or suggest improvements!
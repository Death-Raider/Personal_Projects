# Project Idea
- The aim of this project was to understand the concept of:
  - Data Collection
  - Data augmentation
  - Neural Network Working
  - Front-End (CSS, HTML, JS) workflow
  - Back-End (Node.js, Python) workflow
  - Database management services (MongoDB)

# Execution
- The project ahs been divided into two parts based on the type of work.
  - Data Collection
  - Data Prediction
  
### Data Collection
- Data collection was done by creating a website with an attractive front end where the user can draw an image and the label it as well.
- The data is checked once by the server to ensure it is a number; the checking involves
  - Comparing with existing value in the database (meta classification)
  - Checking if number of set values of the drawn image lie in a range
- The values are then stored in a mongoDB cluster
### Data Prediction
- Using my own library [@death-raider/Neural-Network](https://www.npmjs.com/package/@death_raider/neural-network), I trained a neural network on the data stored in the database
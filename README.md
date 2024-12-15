# NASA Earth Data Visualization: Droughts and Floods  

This project visualizes **drought** and **flood** data using NASA Earth datasets. It processes and serves geospatial data for interactive visualization through a local server. The implementation involves parsing large datasets, efficient data management, and rendering visualizations on a web interface.  

---

## **Features**  

1. **Drought Visualization**:  
   - Parses and displays drought-related data from the NASA dataset.  
   - Processes geospatial ASCII Grid files (`.asc`) into smaller chunks for efficient visualization.  

2. **Flood Visualization**:  
   - Handles flood data in a similar manner to drought data.  
   - Parses large `.asc` files and serves the parsed data for rendering on a web interface.  

---

## **How to Run the Project**  

**Skip to Step 4 if newData directory has values**

### **Step 1: Extract Dataset**  
Extract the `gddrg.zip` file into the same directory as `parseData.js`, `server.js`, and `test.js`.  

### **Step 2: Prepare Data for Parsing**  
Ensure the **`newData/` folder** is created and empty. This folder will store the parsed data as smaller text files.  

### **Step 3: Parse Data**  
Run `parseData.js` to process the large `.asc` files into smaller chunks. Ensure your system has at least **5 GB of RAM** available.  
- Open `parseData.js` to check or customize the specific command for execution.  
- The script parses the `gddrg.asc` files and outputs **10 text files** into the `newData/` folder.  

### **Step 4: Start the Server**  
Run `server.js` to start a local Node.js server. The server reads the parsed data files from the `newData/` folder.  

### **Step 5: Visualize Data**  
- Open your browser and navigate to **`localhost:3000`**.  
- The web interface renders the drought or flood visualizations using the served data.  

---

## **Technical Workflow**  

### **1. Data Parsing (parseData.js)**  
- Processes large `.asc` files (ASCII Grid format) into manageable chunks.  
- Splits data into **10 text files**, each containing a portion of the geospatial data for easy rendering.  

### **2. Server Setup (server.js)**  
- Serves the parsed data using a Node.js server.  
- Dynamically reads data from the `newData/` folder and streams it to the web client.  

### **3. Web Interface (test.js)**  
- Renders the visualizations for drought and flood data.  
- Uses geospatial libraries to plot data interactively on a map.  

---

## **Notes and Requirements**  

1. **System Requirements**:  
   - At least **5 GB of RAM** is required for running `parseData.js`.  
   - Ensure sufficient disk space for extracted and processed files.  

2. **Dependencies**:  
   - Node.js (for running `server.js` and `parseData.js`).  
   - Libraries used in `test.js` for client-side visualization (e.g., D3.js or Leaflet.js).  

3. **Dataset Format**:  
   - The `.asc` files are NASA Earth geospatial data in ASCII Grid format.  

---

## **Future Improvements**  

1. **Interactive Maps**:  
   - Add zoom and filter functionality for better exploration of drought and flood regions.  

2. **Real-Time Updates**:  
   - Automate fetching and parsing of updated NASA datasets.  

3. **Performance Optimization**:  
   - Implement data caching and reduce memory usage during parsing.  

4. **Deployment**:  
   - Deploy the server on a cloud platform for public access.  

5. **Analytics Dashboard**:  
   - Integrate visual analytics (e.g., trend graphs) to complement map-based visualization.  

This project offers a foundation for efficiently visualizing large-scale geospatial data and highlights key climate phenomena like droughts and floods.
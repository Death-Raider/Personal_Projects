# BlackCoffer Webscraping Assignment

## Overview

This project focuses on scraping text data from multiple web pages and performing text analysis to calculate 13 specific metrics. The approach involves a combination of **JavaScript prototyping**, **Selenium-based automation**, and **Python scripting** for text processing and metric calculations.

---

## Approach

1. **Prototype Solution**:
   - Open a target link and identify the appropriate HTML class containing the required text.
   - Write a JavaScript solution to extract the text.

2. **Automate with Selenium**:
   - Implement the JavaScript code using **Selenium** to automate the extraction process.
   - Extract text content from all provided links.

3. **Text Processing**:
   - Create a class to clean and process the extracted text.
   - Calculate the 13 metrics for text analysis.

4. **Batch Execution**:
   - Repeat the extraction and analysis process for all links provided in the `Input.xlsx` file.

---

## Instructions

1. **Prepare Files**:
   - Place the following files in the same directory:
     - `Input.xlsx`: Contains the input URLs.
     - `Output Data Structure.xlsx`: Defines the structure of the output file.
     - `TextAnalysis.py`: Python script to perform text extraction and analysis.
   - Ensure the `MasterDictionary` and `StopWords` directories are also in the same directory for text processing.

2. **Install Dependencies**:
   - Install required libraries by running:
     ```bash
     pip install -r requirements.txt
     ```

3. **Download NLTK Data**:
   - Run the following in a Python environment to download the necessary NLTK data:
     ```python
     import nltk
     nltk.download('punkt')
     ```

4. **Run the Script**:
   - Execute the `TextAnalysis.py` script:
     ```bash
     python TextAnalysis.py
     ```
   - The script will process all the links and generate an output file, `Output.xlsx`, with the calculated metrics.

---

## Output

The script produces an `Output.xlsx` file that contains:
- Extracted text from the provided URLs.
- Calculated metrics for text analysis, as per the `Output Data Structure.xlsx`.

---

## Dependencies

1. **Selenium**:
   - For web automation and text extraction.
   - Requires **ChromeDriver** (compatible with your Chrome version).

2. **Pandas**:
   - For handling data from `Input.xlsx` and exporting results to `Output.xlsx`.

3. **NLTK**:
   - For tokenizing text and processing natural language data.

---

## Additional Notes

- Ensure that **ChromeDriver** is correctly set up and accessible in your system's PATH for Selenium to work.
- The `MasterDictionary` and `StopWords` directories should contain the necessary files required for text cleaning and analysis.
- The script will process links sequentially. Depending on the number of links, execution time may vary.

---

## License
This project is licensed under the MIT License. Feel free to modify and adapt it as needed.
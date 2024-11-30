# Approach
* Open a link and find out the appropriate class containing the text
* Prototype a solution in javascript
* Using Selenium, implement the JS code
* Created a class to modify the extracted text and calculate the 13 metrics
* Repeat for all links

# Instructions:
* Keep "Input.xlsx", "Output Data Structure.xlsx" and "TextAnalysis.py" in same directory
* Keep MasterDictionary and StopWords dictionaries in the same directory
* Install requirements via the requirements.txt
* Additionally run once:
```py
import nltk
nltk.download('punkt')
```
* Run "TextAnalysis.py" and wait
* Output.xlsx is generated
* 
# Dependancies:
1. selenium
	chromdriver ( for selenium )
2. pandas
3. nltk
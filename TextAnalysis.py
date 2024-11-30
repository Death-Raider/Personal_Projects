from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

import os

from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
# nltk.download('punkt')

class Text_Anlysis():
    def __init__(self,stop_words_df,posneg_word_df):
        self.stopWordDF = stop_words_df
        self.posNegWordDF = posneg_word_df
        self.words_removed = 0
        self.posNegWordCounts = 0
        self.percentComplexWords = 0
        self.complexWordCount = 0
        self.averageSentenceLength = 0
        self.personalPronounCount = 0
        self.syllableCount = 0
        self.syllableCountPerWord = 0
        self.fogIndex = 0
        self.averageWordLength = 0
        self.wordCount = 0

    def textAnalysis(self,text: str):
        flat = lambda x: [item for subarr in x for item in subarr]
        sentences = sent_tokenize(text)
        print("Tokenized by sentences")
        pattern = r"\w+"
        tokenizer = nltk.RegexpTokenizer(pattern)
        for i in range(len(sentences)):
            sentences[i] = tokenizer.tokenize(sentences[i])
        print("Tokenized sentence by words")

        words = flat(sentences)
        removed_stop_words = self.removeStopWords(words)
        print("Removed sop words")
        self.sementicAnalysis(removed_stop_words)
        print("sementic analysis done")
        self.wordCounter(removed_stop_words)
        print("count of words done")

        self.wordCount = len(words)
        self.averageWordLength = sum([len(w) for w in words]) / self.wordCount
        self.averageSentenceLength = len(words) / len(sentences)
        self.percentComplexWords = self.complexWordCount / len(sentences)
        self.fogIndex = 0.4*(self.averageSentenceLength + self.percentComplexWords)
        print("metrics calculated")

    def removeStopWords(self,text: list[str])->list[str]:
        print(len(text))
        for i,stopWord in enumerate(self.stopWordDF['value']):
            try:
                text.remove(stopWord)
            except:
                continue
            else:
                self.stopWordDF.iloc[i,2] += 1
        self.words_removed = self.stopWordDF['count'].sum()
        print(len(text))
        return text

    def sementicAnalysis(self,text:list[str])->None:
        for i,Word in enumerate(self.posNegWordDF['value']):
            try:
                text.index(Word)
            except:
                continue
            else:
                self.posNegWordDF.iloc[i,2] += 1
        self.posNegWordCounts = self.posNegWordDF.groupby('class')["count"].sum()

    def wordCounter(self,output:str)->None:
        for i,word in enumerate(output):
            if word.lower() in ["i", "me", "ours", "us", "we"] and word != "US" :
                self.personalPronounCount += 1

            if (word[-2:] != 'ed' or word[-2:] != 'es'):
                localCounter = 0
                for ch in word:
                    if ch in 'aeiou':
                        localCounter += 1
                self.syllableCount += localCounter
                if localCounter > 2:
                    self.complexWordCount += 1
        self.syllableCountPerWord = self.syllableCount / len(output)

# Get data for text analysis
def get_stop_word_df(fpath):
    allWords = None
    for path, directories, files in os.walk(fpath):
        for file in files:
            word_table = pd.read_table(path+file, sep="|", names=["value", "class", "count"], encoding='latin-1', converters={'value': lambda x: x if x == 'NULL' else x})
            word_table.fillna({"class":-1,"count":0},inplace=True)
            for i in range(0,len(word_table)):
                    word_table.iloc[i,1] = word_table.iloc[i-1,1] if word_table.iloc[i,1] == -1 else word_table.iloc[i,1]
            allWords = pd.concat((allWords,word_table))
    return allWords
def get_positive_negative_word_df(fpath):
    allWords = None
    for path,directoroies,files in os.walk(fpath):
        for i,file in enumerate(files):
            word_table = pd.read_table(path+file, sep=",", names=["value", "class","count"], encoding='latin-1')
            word_table.fillna({"class":i,"count":0},inplace=True)
            allWords = pd.concat((allWords,word_table))
    return allWords

# Get text from the url
def extract_text_from_url(browser, url: str) -> str:
    output_str = ""
    browser.get(url)
    element_present = EC.presence_of_element_located((By.CLASS_NAME,"td-post-content.tagdiv-type"))
    WebDriverWait(browser, 2).until(element_present)
    paragraph = browser.find_elements(By.CLASS_NAME,"td-post-content.tagdiv-type")[0]
    children = paragraph.find_elements(By.XPATH,"./child::*")
    for child in children:
        output_str += child.text.strip()
        output_str += "\n"
    return output_str

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
# option.add_argument('--headless=new')
option.add_argument("--disable-gpu")
browser = webdriver.Chrome(options=option)

input_data = pd.read_excel("Input.xlsx")
output_data = pd.read_excel("Output Data Structure.xlsx")
print(input_data.head(5))
print(output_data.head(5))
print()

stop_words_df = get_stop_word_df("StopWords/")
pos_neg_df = get_positive_negative_word_df("MasterDictionary/")

print(stop_words_df)
print()

print(pos_neg_df)
print()
for URLindex in range(0,len(input_data)):
    # URLindex = 10
    url = input_data["URL"][URLindex]
    output_text = []

    try:
        output_text.append(extract_text_from_url(browser,url))
    except:
        continue

    TA = Text_Anlysis(stop_words_df,pos_neg_df)
    TA.textAnalysis(output_text[0])

    outputValues = [
        TA.posNegWordCounts.iloc[1],
        TA.posNegWordCounts.iloc[0],
        (TA.posNegWordCounts.iloc[1]-TA.posNegWordCounts.iloc[0]) / (TA.posNegWordCounts.iloc[1]+TA.posNegWordCounts.iloc[0]+ 0.000001),
        (TA.posNegWordCounts.iloc[1]+TA.posNegWordCounts.iloc[0]) / (TA.wordCount + 0.000001),
        TA.averageSentenceLength,
        TA.percentComplexWords,
        TA.fogIndex,
        TA.averageSentenceLength,
        TA.complexWordCount,
        TA.wordCount,
        TA.syllableCountPerWord,
        TA.personalPronounCount,
        TA.averageWordLength
    ]
    for ind in range(0,13):
        output_data.iloc[URLindex,2+ind] = outputValues[ind]

    print(URLindex)

output_data.to_excel("Output.xlsx")
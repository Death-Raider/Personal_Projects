from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from random import normalvariate

def normal_choice(lst, mean=None, stddev=None):
    if mean is None:
        mean = (len(lst) - 1) / 2

    if stddev is None:
        stddev = len(lst) / 8

    while True:
        index = int(normalvariate(mean, stddev) + 0.5)
        if 0 <= index < len(lst):
            return lst[index]

option = webdriver.ChromeOptions()
option.add_argument("--incognito")
option.add_experimental_option("detach", True)
option.add_argument('--headless=new')
option.add_argument("--disable-gpu")

browser = webdriver.Chrome(options=option)
browser.get("url_of_gform")

# find class name from inspect
class_for_submit = "NPEfkd" 
class_for_radial_buttons = "AB7Lab" 

for _ in range(200):
    radiobuttons = browser.find_elements(By.CLASS_NAME,class_for_radial_buttons)
    submitbutton = browser.find_elements(By.CLASS_NAME,class_for_submit)
    choices = {'0':0,'1':0,'2':0,'3':0,'4':0}
    try:
        for i in range(25):
            index = normal_choice([0,1,2,3,4])
            choices[str(index)] += 1
            radiobuttons[i*5+index].click()
        print(choices)
        submitbutton[1].click()
        time.sleep(2)
        browser.find_element(By.LINK_TEXT,"Submit another response").click()
    except:
        print("Error Occured. Clearing form and retrying")
        submitbutton[2].click() # clear form
        submitbutton = browser.find_elements(By.CLASS_NAME,class_for_submit)
        submitbutton[6].click() # confirm clearing
        continue
browser.close()
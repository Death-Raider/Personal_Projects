from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def start_browser():
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    # option.add_argument('--headless=new')
    option.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=option)
    return browser
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
    option.add_argument("--headless")  # Run in headless mode
    option.add_argument("--no-sandbox")  # Bypass OS security model
    option.add_argument("--disable-dev-shm-usage")  # Overcome shared memory issue
    option.add_argument("--disable-gpu")  # Disable GPU rendering
    option.add_argument("--disable-extensions")  # Disable extensions
    option.add_argument("--disable-software-rasterizer")  # Disable unnecessary rendering
    option.add_argument("--remote-debugging-port=9222")  # Debugging port (optional)
    browser = webdriver.Chrome(options=option)
    return browser
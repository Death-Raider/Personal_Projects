from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

option = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": os.getcwd(),
    "download.prompt_for_download": False,       # don't ask where to save
    "download.directory_upgrade": True,          # overwrite if dir exists
    "safebrowsing.enabled": True,                # allow safe download
}
option.add_experimental_option("prefs", prefs)
option.add_argument("--incognito")
option.add_argument("--headless=new")
option.add_argument("--no-sandbox")
option.add_argument("--disable-dev-shm-usage")
option.add_argument("--disable-gpu")
browser = webdriver.Chrome(options=option)

browser.execute_cdp_cmd(
    "Page.setDownloadBehavior",
    {
        "behavior": "allow",
        "downloadPath": prefs["download.default_directory"],
    },
)

url = "https://ida.loni.usc.edu/login.jsp"

browser.get(url)
print("Got URL")

def find_element_click(by, value, wait=True):
    if wait:
        ele_present = EC.element_to_be_clickable((by,value))
        ele = WebDriverWait(browser, 10).until(ele_present)
    else:
        ele = browser.find_element(by, value)
    if ele:
        try:
            ele.click()
        except:
            try:
                browser.execute_script("arguments[0].click();", ele)
            except:
                print("Cannot Click, try again")
                return -1, None
    return 1, ele

find_element_click(By.CLASS_NAME, "ida-cookie-policy-accept") # accept cookie
print("Accepted Cookie")
time.sleep(5)

_, elem = find_element_click(By.CLASS_NAME, "ida-user-menu-icon", wait=False)
print("Clicked on LogIn menu")
time.sleep(1)


_, user_email = find_element_click(By.NAME, "userEmail", wait=False) # username
user_email.clear()
user_email.send_keys("YOUR_GMAIL@gmail.com")
print("Entered User Email")
_, user_passwd = find_element_click(By.NAME, "userPassword", wait=False) # paswd
user_passwd.clear()
user_passwd.send_keys("YOUR_PASSWORD")
print("Entered User Password")

time.sleep(1)

ret,_ = find_element_click(By.CLASS_NAME, "login-loader", wait=False) # log in
print("Loggin In")
while ret < 0:
    ret,_ = find_element_click(By.CLASS_NAME, "login-loader", wait=False) # log in
print("Logged In")
time.sleep(5)

browser.get("https://ida.loni.usc.edu/pages/access/search.jsp?project=ADNI&tab=collection&page=SEARCH&subPage=NEW_ADV_QUERY")
print("Got new URL")
time.sleep(5)

find_element_click(By.ID, "ygtvlabelel1", wait=False) # click on "my collection"
print("Clicked on My Collection")
time.sleep(1)

find_element_click(By.ID, "ygtvlabelel5", wait=False) # click on "ADNI"
print("Clicked on ADNI")
time.sleep(1)

find_element_click(By.ID, "ygtvlabelel6", wait=False) # click on "Not Downloaded"
print("Clicked on Not Downloaded")
time.sleep(5)

find_element_click(By.NAME, "selectAll", wait=False)
print("Clicked on selectAll")
time.sleep(5)

find_element_click(By.ID, "simple-download-button", wait=False)
print("Clicked on 1-Click Download")
time.sleep(30)

print("Now Downloading Metadata")
ret, elem = find_element_click(By.CLASS_NAME, "simple-download-metadata-link-text", wait=False)
print("download link (if needed):", elem.get_attribute("href"))
time.sleep(5)
print("Now Downloading Data")
ret, elem = find_element_click(By.CLASS_NAME, "simple-download-download-link", wait=False)
print("download link (if needed):", elem.get_attribute("href"))

# Automated Data Download from IDA LONI (ADNI)

This script automates the login and dataset download process from the [IDA LONI platform](https://ida.loni.usc.edu/) using Selenium with Chrome in headless mode.
It is specifically designed to:

1. Log in to the IDA portal.
2. Navigate to the ADNI "Not Downloaded" section.
3. Select all files and start the **1-Click Download** process.
4. Download both metadata and data files directly to the working directory without user prompts.

---

## Features

* **Headless Chrome**: Runs without a GUI, ideal for servers or cloud VMs.
* **Automatic download handling**: Uses Chrome DevTools protocol to bypass download popups.
* **Element interaction helper**: `find_element_click()` waits and safely clicks page elements.
* **Progress logging**: Prints key actions to the console.
* **Auto-selection of "Not Downloaded" data** for quick dataset retrieval.

---

## Prerequisites

### Python Environment

* Python 3.8+
* Install packages:

```bash
pip install selenium
```

### Chrome and Chromedriver

Make sure Google Chrome and the matching ChromeDriver are installed and accessible in `PATH`.

---

## How to Use

1. Clone or copy this script to your server or local machine.
2. Replace these lines with your **IDA portal credentials**:

```python
user_email.send_keys("YOUR_GMAIL@gmail.com")
user_passwd.send_keys("YOUR_PASSWORD")
```

3. Run the script:

```bash
python your_script.py
```

All downloaded files will be saved to the **current working directory** where you run the script.

---

## Key Code Sections

### 1. Chrome Options

The script configures Chrome to:

* Use **incognito** and **headless mode**
* Automatically save downloads to the current directory
* Bypass any download confirmation dialogs:

```python
option.add_experimental_option("prefs", prefs)
option.add_argument("--headless=new")
option.add_argument("--no-sandbox")
option.add_argument("--disable-dev-shm-usage")
browser.execute_cdp_cmd(
    "Page.setDownloadBehavior",
    {
        "behavior": "allow",
        "downloadPath": prefs["download.default_directory"],
    },
)
```

### 2. `find_element_click()` helper

This function tries to locate an element, waits if needed, and clicks it safely:

```python
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
```

### 3. Navigation Flow

* Accept cookies
* Open login menu
* Enter email and password
* Go to ADNI → Not Downloaded → Select All → 1-Click Download
* Download Metadata & Data

---

## Output

* Downloads all selected files to the current directory.
* Prints metadata and dataset download URLs (for debugging or logging).

---

## Notes

* Make sure your IDA account has permissions to access the ADNI data.
* The script relies on specific element IDs/classes from the IDA portal.
  If the website changes, these locators may need updates.
* Avoid hardcoding credentials in shared code.

---

## License

This script is for personal/research use. Please comply with the data usage policies of IDA/ADNI.


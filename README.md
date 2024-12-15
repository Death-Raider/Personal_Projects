# HTML Grid Layout Generator

This Python script generates an HTML grid layout based on the data provided in a JSON file. It creates a responsive grid where elements are positioned according to specified bounding boxes, allowing for easy customization of layout and styles.

## Features
- Load layout data from a JSON file.
- Create an HTML grid layout with customizable granularity.
- Automatically positions elements based on specified coordinates and dimensions.
- Generates a complete HTML file that can be viewed in any web browser.

## Requirements

- Python 3.x
- `json` library (included in the standard library)

## Setup

1. Clone the repository (if applicable) or download the script.
```bash
   git clone html_template
   cd html_template
```

2. Ensure you have Python installed. You can download it from https://www.python.org/downloads/.

3. Prepare your JSON data file (data.json) with the following structure:
```json
   {
       "width": 1600,
       "height": 662,
       "bounding_boxes": [
           {
               "class": "h1",
               "xywh": [0.1, 0.2, 0.1, 0.1],
               "data": "Heading 1",
               "color": "#FF0000"
           },
           {
               "class": "h2",
               "xywh": [0.15, 0.2, 0.1, 0.1],
               "data": "Heading 2",
               "color": "#00FF00"
           }
       ]
   }
```
Modify the data.json file to fit your layout needs.

## Usage

1. Run the script:
```bash
   python html_creater.py
```
2. After running the script, an HTML file named test.html will be generated in the same directory.

3. Open test.html in a web browser to view the generated grid layout.

## Functions

1. load_data(json_path: str) -> dict
    - Loads the JSON data from the specified file.

2. create_element_html(data: dict, granularity: int | list[int]) -> str

   - Creates the HTML structure for the grid layout based on the data and specified granularity.

3. main()

   - Main function that orchestrates loading the data and generating the HTML file.

## Customization

- You can adjust the granularity of the grid by modifying the parameters in the create_element_html function call in the main function.
- Customize the bounding boxes in the data.json file to change the content and layout.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


import json
from jsonDataValidator import JSONValidator
def load_data(json_path: str)->dict:
    template = {
        "height": int,
        "width" : int,
        "bounding_boxes" : list
    }
    data = {}
    try:
        with open(json_path, "r") as f:
            data = json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading JSON: {e}")
    
    validator = JSONValidator(template,data)
    try:
        validator.is_valid()
        print("data is valid and parsed successfully")
        return data
    except (KeyError, TypeError) as e:
        print(f"Error loading data: {e}")
        print(f"Expected Format: {template}")
        return None

def create_element_html(data:dict, granularity:int|list[int])->str: 
    website_height = f"{int(data['height'])}px"
    website_width = f"{int(data['width'])}px"

    if isinstance(granularity,int):
        GRID_X = granularity
        GRID_Y = granularity
    elif isinstance(granularity,list) or isinstance(granularity,tuple):
        GRID_X = granularity[0]
        GRID_Y = granularity[1]
    else:
        raise ValueError("Granularity can only be int, list[int] or tuple[int]")

    wrapper_div = f"""
    <div id="website_part" style="
        width: {website_width};
        height: {website_height};
        display: grid;
        background-color: #ff96f8AA;
        grid-template-columns: repeat({GRID_X}, 1fr);
        grid-template-rows: repeat({GRID_Y}, 1fr);
    ">
    """

    for i in range(len(data["bounding_boxes"])):
        box = data["bounding_boxes"][i]
        points = box['xywh']
        col_start = int(points[0] * GRID_X) + 1  # X position in grid (1-indexed)
        row_start = int(points[1] * GRID_Y) + 1  # Y position in grid (1-indexed)
        col_width = int(points[2] * GRID_X)  # Width in Grid
        row_height = int(points[3] * GRID_Y)  # Height in Grid

        # background-color: {box['color']};
        wrapper_div += f"""
        <{box['class']} style="
            grid-column: {col_start} / span {col_width};
            grid-row: {row_start} / span {row_height};
            overflow: hidden;
            height: 100%;
            width: 100%;
            border: solid;
            margin: 0 auto;
            padding: 0;
        ">
            {box['class']}
        </{box['class']}>
        """
    wrapper_div += "</div>"

    return wrapper_div

def main():

    data = load_data("data.json")
    wrapper_div = create_element_html(data,(1000,1000))

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Define the property of the wrapper div for the data elements -->   
    </head>
    <body>
    {wrapper_div}
    </body>
    </html>
    """

    with open("test.html", "w") as f:
        f.write(html_content)

main() # run main function 
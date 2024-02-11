import json
import re
from llama_index import Document
import csv

def filter_keys_in_dicts(dict_list, keys_to_keep):
    """
    Filters a list of dictionaries by keeping only certain keys.

    :param dict_list: List of dictionaries.
    :param keys_to_keep: List of keys to keep in the dictionaries.
    :return: A new list of dictionaries containing only the specified keys.

    Example:
    data = [
        {'name': 'John', 'age': 30, 'city': 'New York'},
        {'name': 'Jane', 'age': 25, 'city': 'Los Angeles'},
        {'name': 'Bob', 'age': 35, 'city': 'Chicago'}
    ]

    keys_to_keep = ['name', 'age']

    filtered_data = filter_keys_in_dicts(data, keys_to_keep)
    print(filtered_data)
    
    """
    filtered_list = []
    for d in dict_list:
        filtered_dict = {key: d[key] for key in keys_to_keep if key in d}
        filtered_list.append(filtered_dict)
    return filtered_list


def save_json(file_path: str, data: dict):
    """
    Save a dictionary as JSON to a file.

    Args:
        file_path (str): The path of the file to save the JSON data to.
        data (dict): The dictionary to be saved as JSON.

    Raises:
        IOError: If there is an error while writing the JSON data to the file.

    Example:
        >>> data = {'name': 'John', 'age': 30}
        >>> save_json('/path/to/file.json', data)
    """
    # Convert the data dictionary to JSON format
    json_data = json.dumps(data)

    # Save the JSON data to the file
    try:
        with open(file_path, "w") as file:
            file.write(json_data)
    except IOError as e:
        raise IOError(f"Error while saving JSON data to file: {str(e)}")

def strip_html(content):
    """
    Remove HTML tags from the given content string.

    Args:
    content (str): A string containing HTML content.

    Returns:
    str: The content string with all HTML tags removed.
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', content)

def ignore_key(dictionary, key):
    new_dict = dictionary.copy()
    del new_dict[key]
    return new_dict


def filter_dict(d):
    allowed_types = (str, int, float)
    return {k: v for k, v in d.items() if isinstance(v, allowed_types)}

def create_document(text: str, metadata: dict, metadata_to_exclude: list) -> Document:
    document = Document(
        text=text,
        metadata=metadata,
        excluded_llm_metadata_keys=metadata_to_exclude,
        metadata_seperator="::",
        metadata_template="{key}=>{value}",
        text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
    )
    return document

def load_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data

import random, string, json, os

def create_random_string(char_nr):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_nr))

def read_data_from_json(file_name):
    """
    Parse json
    :param file_name: json file
    :return: parsed json
    """
    directory = os.path.dirname(__file__)
    filename = os.path.join(directory, '../test_data/'+file_name)

    with open(filename) as f:
        json_data = f.read()
        return json.loads(json_data)
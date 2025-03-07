import json
import os
from datetime import datetime
from functools import wraps

class JsonHandler:
    def __init__(self, file_path):
        """
        Initialize the JsonHandler class with the given file path.
        """
        self.file_path = file_path

    def _load_json(self):
        """
        Load JSON data from the file if it exists, otherwise return an empty dictionary.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def _save_json(self, data):
        """
        Save the provided data into the JSON file.
        """
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def create_or_update_date(self):
        """
        Create the JSON file with only the 'date' key if it doesn't exist,
        or update the 'date' if it has changed.
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        # current_date = "2024-12-12"
        data = self._load_json()

        if data.get('date') != current_date:
            print(f"Date updated to {current_date}")
            data = {'date': current_date}  # Reset all data, keeping only the updated date
        else:
            print(f"Date remains the same: {current_date}")

        self._save_json(data)

    def update_data(self, updates):
        """
        Update the JSON file with the given key-value pairs.
        """
        data = self._load_json()
        data.update(updates)
        self._save_json(data)
        print(f"Updated the following records: {updates}")

    def fetch_json(self):
        """
        Fetch and return the entire JSON data.
        """
        return self._load_json()

    def json_decorator(self):
        """
        A decorator function to fetch JSON data before executing a function.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Fetch the JSON data
                json_data = self.fetch_json()

                # Add the JSON data to the wrapped function's arguments
                kwargs['json_data'] = json_data
                print(f"Fetched JSON data: {json_data}")
                # Execute the wrapped function
                return func(*args, **kwargs)

            return wrapper

        return decorator

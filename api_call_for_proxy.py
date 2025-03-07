import requests

class IcelandCamSysAPI:
    def __init__(self, base_url, default_headers=None):
        """
        Initialize the API client.
        :param base_url: Base URL of the API.
        :param default_headers: Default headers to use for all requests.
        """
        self.base_url = base_url
        self.headers = default_headers or {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def make_request(self, endpoint, method, json_data=None):
        """
        Make an API request.
        :param endpoint: API endpoint to call (relative to the base URL).
        :param method: HTTP method ('GET', 'POST', 'PUT', etc.).
        :param json_data: JSON payload to send with the request.
        :return: Response object.
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=json_data, verify=false)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()  # Return JSON data if available
        except requests.exceptions.RequestException as e:
            print(f"Error during {method} request to {url}: {e}")
            return None
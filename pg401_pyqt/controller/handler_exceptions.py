import requests

def handler_exeptions(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        print("A Connection error occurred.", e)
    elif isinstance(e, requests.exceptions.HTTPError):
        print("An HTTP error occurred.", e)
    elif isinstance(e, requests.exceptions.Timeout):
        print("The request timed out.", e)
    elif isinstance(e, requests.exceptions.RequestException):
        print("Another exception occurred", e)
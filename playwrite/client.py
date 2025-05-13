import requests

# Define the server URL
server_url = "http://localhost:8123"

# Example: Navigate to a URL
navigate_payload = {
    "tool": "playwright_navigate",
    "params": {"url": "https://example.com"}
}
response = requests.post(server_url, json=navigate_payload)
print(response.json())

# Example: Click an element by selector
click_payload = {
    "tool": "playwright_click",
    "params": {"selector": "#submit-button"}
}
response = requests.post(server_url, json=click_payload)
print(response.json())

# Example: Fill an input field
fill_payload = {
    "tool": "playwright_fill",
    "params": {
        "selector": "#email",
        "value": "user@example.com"
    }
}
response = requests.post(server_url, json=fill_payload)
print(response.json())

# Example: Take a screenshot
screenshot_payload = {
    "tool": "playwright_screenshot",
    "params": {"name": "example.png"}
}
response = requests.post(server_url, json=screenshot_payload)
print(response.json())

# Example: Get text content from the page
get_text_payload = {
    "tool": "playwright_get_text_content",
    "params": {}
}
response = requests.post(server_url, json=get_text_payload)
print(response.json())

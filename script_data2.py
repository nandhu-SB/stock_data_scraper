import requests
from bs4 import BeautifulSoup

# Initialize a session
session = requests.Session()

# Define login credentials
login_url = "https://example.com/login"
credentials = {
    "username": "nandhuesbee95@gmail.com",
    "password": "Goodmorningmadam95."
}

# Log in
response = session.post(login_url, data=credentials)
if response.status_code == 200 and "logout" in response.text.lower():
    print("Login successful!")
else:
    print("Login failed.")
    exit()

# Access a protected page
protected_url = "https://example.com/protected-page"
protected_page = session.get(protected_url)

# Parse the page
soup = BeautifulSoup(protected_page.content, "html.parser")
print(soup.prettify())

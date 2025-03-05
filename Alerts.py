import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
import os

# Function to scrape individual terrorists list
def scrape_individual_terrorists(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        names = []
        for item in soup.find_all('li'):  # Adjust tag/class
            names.append(item.text.strip())
        return names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []

# Function to scrape terrorist organizations list
def scrape_terrorist_organizations(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        names = []
        for item in soup.find_all('li'):  # Adjust tag/class
            names.append(item.text.strip())
        return names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []

# Function to scrape unlawful associations list
def scrape_unlawful_associations(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        names = []
        for item in soup.find_all('li'):  # Adjust tag/class
            names.append(item.text.strip())
        return names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []

# Function to scrape the UN sanctions list (XML)
def scrape_un_sanctions(xml_url):
    try:
        response = requests.get(xml_url)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        names = []
        for entity in root.findall('.//member'):  # Adjust based on XML structure
            name = entity.find('name')
            if name is not None:
                names.append(name.text.strip())
        return names
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {xml_url}: {e}")
        return []

# Function to send email notifications
def send_email(subject, body):
    sender = os.getenv('OUTLOOK_EMAIL')
    recipient = os.getenv('RECIPIENT_EMAIL')
    email_password = os.getenv('OUTLOOK_PASSWORD')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP('smtp.gmail.com', 465) as server:
        server.starttls()
        server.login(sender, email_password)
        server.sendmail(sender, recipient, msg.as_string())

# Compare current data with stored data and check for changes
def compare_and_notify(current_names, previous_names, source_name):
    additions = set(current_names) - set(previous_names)
    removals = set(previous_names) - set(current_names)

    if additions or removals:
        subject = f"Name Changes Detected: {source_name}"
        body = f"Additions: {', '.join(additions)}\nRemovals: {', '.join(removals)}"
        send_email(subject, body)

# Main logic
def main():
    urls = {
        "Individual Terrorists": "https://www.mha.gov.in/en/page/individual-terrorists-under-uapa",
        "Terrorist Organizations": "https://www.mha.gov.in/en/commoncontent/list-of-organisations-designated-%E2%80%98terrorist-organizations%E2%80%99-under-section-35-of",
        "Unlawful Associations": "https://www.mha.gov.in/en/commoncontent/unlawful-associations-under-section-3-of-unlawful-activities-prevention-act-1967",
        "UN Sanctions List": "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
    }

    for source_name, url in urls.items():
        if source_name == "UN Sanctions List":
            current_names = scrape_un_sanctions(url)
        elif source_name == "Individual Terrorists":
            current_names = scrape_individual_terrorists(url)
        elif source_name == "Terrorist Organizations":
            current_names = scrape_terrorist_organizations(url)
        else:
            current_names = scrape_unlawful_associations(url)

        try:
            with open(f'previous_{source_name}.txt', 'r') as f:
                previous_names = f.read().splitlines()
        except FileNotFoundError:
            previous_names = []

        compare_and_notify(current_names, previous_names, source_name)

        with open(f'previous_{source_name}.txt', 'w') as f:
            f.write("\n".join(current_names))

if __name__ == '__main__':
    main()

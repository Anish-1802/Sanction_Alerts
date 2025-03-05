import smtplib
from email.mime.text import MIMEText
import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Fetch the environment variables
sender = os.getenv('GMAIL_EMAIL')
email_password = os.getenv('GMAIL_APP_PASSWORD')  # Use the app password here
recipient = os.getenv('RECIPIENT_EMAIL')

# Function to scrape individual terrorists list
def scrape_individual_terrorists(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    names = []
    
    # Example logic to scrape names; adjust based on actual HTML structure
    for item in soup.find_all('li'):  # Replace with actual tag/class to identify names
        names.append(item.text.strip())

    return names

# Function to scrape terrorist organizations list
def scrape_terrorist_organizations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    names = []
    
    # Example logic to scrape organizations; adjust based on actual HTML structure
    for item in soup.find_all('li'):  # Replace with actual tag/class to identify organizations
        names.append(item.text.strip())

    return names

# Function to scrape unlawful associations list
def scrape_unlawful_associations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    names = []
    
    # Example logic to scrape associations; adjust based on actual HTML structure
    for item in soup.find_all('li'):  # Replace with actual tag/class to identify associations
        names.append(item.text.strip())

    return names

# Function to scrape the UN sanctions list (XML)
def scrape_un_sanctions(xml_url):
    response = requests.get(xml_url)
    root = ET.fromstring(response.text)
    names = []
    
    # Loop through XML to extract names of individuals/entities
    for entity in root.findall('.//member'):  # Adjust based on XML structure
        name = entity.find('name').text
        if name:
            names.append(name.strip())

    return names

# Function to send email notifications
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        # Using SMTP_SSL for port 465 (secure connection)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, email_password)  # Login with the app password
            server.sendmail(sender, recipient, msg.as_string())  # Send email
            print("Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication error: {e}")
    except smtplib.SMTPServerDisconnected as e:
        print(f"SMTP Server disconnected: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

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
    # URLs of websites
    urls = {
        "Individual Terrorists": "https://www.mha.gov.in/en/page/individual-terrorists-under-uapa",
        "Terrorist Organizations": "https://www.mha.gov.in/en/commoncontent/list-of-organisations-designated-%E2%80%98terrorist-organizations%E2%80%99-under-section-35-of",
        "Unlawful Associations": "https://www.mha.gov.in/en/commoncontent/unlawful-associations-under-section-3-of-unlawful-activities-prevention-act-1967",
        "UN Sanctions List": "https://scsanctions.un.org/resources/xml/en/consolidated.xml?_gl=1*1qd0esu*_ga*MTc2NDQ4ODU2NS4xNzQxMDg5OTI3*_ga_TK9BQL5X7Z*MTc0MTE1NTM3MS4yLjAuMTc0MTE1NTM3MS4wLjAuMA.."
    }

    # Scrape data from each URL and compare it with previous data
    for source_name, url in urls.items():
        if source_name == "UN Sanctions List":
            current_names = scrape_un_sanctions(url)
        elif source_name == "Individual Terrorists":
            current_names = scrape_individual_terrorists(url)
        elif source_name == "Terrorist Organizations":
            current_names = scrape_terrorist_organizations(url)
        else:
            current_names = scrape_unlawful_associations(url)

        # Load previous names from a file (stored separately for each list)
        try:
            with open(f'previous_{source_name}.txt', 'r') as f:
                previous_names = f.read().splitlines()
        except FileNotFoundError:
            previous_names = []

        # Compare and notify if changes are found
        compare_and_notify(current_names, previous_names, source_name)

        # Save the current names to file for next comparison
        with open(f'previous_{source_name}.txt', 'w') as f:
            f.write("\n".join(current_names))

if __name__ == '__main__':
    main()

import smtplib
import logging
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Enable debug-level logs
logging.basicConfig(level=logging.DEBUG)

# Set up sender and recipient emails directly in the code
sender = 'anishsawant18.as@gmail.com'  # Your Gmail address
recipient = 'anish.sawant3-v@outlook.com'  # The recipient's email address
email_password = 'kdlnygkkvmwluxky'  # Your Gmail app password (generated via Gmail)

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
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.set_debuglevel(1)  # Enable debug output for smtplib
            print("Connecting to SMTP server...")
            server.login(sender, email_password)
            print("Logged in successfully!")
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(sender, recipient, message)
            print("Email sent successfully!")
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
        "UN Sanctions List": "https://scsanctions.un.org/resources/xml/en/consolidated.xml?_gl=1*1qd0esu*_ga*MTc2NDQ4ODU2NS4xNzQxMDg5OTI3*_ga_TK9BQL5X7Z*MTc0MTE1NTM3MS4yLjAuMTc0MTE1NTM3MS4wLjAuMA.."
    }

    # Scrape data from each URL and compare it with previous data
    for source_name, url in urls.items():
        if source_name == "UN Sanctions List":
            current_names = scrape_un_sanctions(url)
        
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

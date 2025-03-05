import smtplib

sender = 'anishsawant18.as@gmail.com'  # Use your actual Gmail address
recipient = 'anish.sawant3-v@adityabirlacapital.com'  # Use the recipient's email
email_password = 'qlwjtmclluoiyuba'  # Use the app password here

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        print("Connecting to SMTP server...")
        server.login(sender, email_password)
        print("Logged in successfully!")
        
        # Send a test email
        message = "Subject: Test\n\nThis is a test email."
        server.sendmail(sender, recipient, message)
        print("Email sent successfully!")
        
except smtplib.SMTPAuthenticationError as e:
    print(f"SMTP Authentication error: {e}")
except smtplib.SMTPServerDisconnected as e:
    print(f"SMTP Server disconnected: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

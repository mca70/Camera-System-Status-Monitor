from ses_email_sender import EmailSender


def send_mail(message, store_id):
    # Initialize the email sender
    email_sender = EmailSender(
        region="eu-west-2",
        aws_access_key="ok",
        aws_secret_key="GK"
    )

    # List SES identities
    try:
        identities = email_sender.list_identities()
        print("Registered SES identities:", identities)
    except Exception as e:
        print("Error:", e)

    '''message = """
    This message is sent via email of application Monitoring.
    """'''

    # Send an email
    identities.remove('notifications@saigroups.co.uk')
    for email in identities:
        email_sender.send_raw_email(
            source_email="notifications@saigroups.co.uk",
            destination_email=email,
            subject=f"Application Monitoring Not Working Store ID {store_id}",
            html_content=f"""
            <html>
        <body>
        
        <code>
        
          <pre style="background-color:#f8f8f2; padding: 10px; border-radius: 5px; font-family: monospace;">
                <textarea style="background-color:#f8f8f2;" rows="50" cols="50", readonly>
                  {message}
                </textarea>
           </pre>
        
        </code>
        </body>
        </html>
            """
        )
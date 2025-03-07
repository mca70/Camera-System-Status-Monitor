import boto3

class EmailSender:
    def __init__(self, region, aws_access_key, aws_secret_key):
        self.ses_client = boto3.client(
            'ses',
            region_name=region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

    def send_raw_email(self, source_email, destination_email, subject, html_content):
        print(destination_email)
        try:
            response = self.ses_client.send_raw_email(
                Source=source_email,
                Destinations=[destination_email],
                RawMessage={
                    'Data': f"""From: {source_email}
To: {destination_email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/html; charset=UTF-8

{html_content}
"""
                }
            )
            print("Email sent! Message ID:", response['MessageId'])
            return response
        except Exception as e:
            print("Error sending email:", e)
            raise

    def list_identities(self):
        """
        Lists the identities registered in SES (email addresses or domains).
        """
        try:
            response = self.ses_client.list_identities()
            print("Identities:", response['Identities'])
            return response['Identities']
        except Exception as e:
            print("Error listing identities:", e)
            raise
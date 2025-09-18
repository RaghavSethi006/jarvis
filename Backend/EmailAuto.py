import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Union

class EmailController:
    def __init__(self, smtp_server: str, smtp_port: int, 
                 imap_server: str, imap_port: int):
        """
        Initialize with email server settings
        :param smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
        :param smtp_port: SMTP port (e.g., 587 for TLS)
        :param imap_server: IMAP server address (e.g., 'imap.gmail.com')
        :param imap_port: IMAP port (e.g., 993 for SSL)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send_email(self, username: str, password: str, 
                   to_addrs: Union[str, List[str]], subject: str, 
                   body: str, html_body: str = None) -> bool:
        """
        Send an email with optional HTML content
        :param username: Your full email address
        :param password: Email account password/app-specific password
        :param to_addrs: Single or list of recipient email addresses
        :param subject: Email subject
        :param body: Plain text email body
        :param html_body: HTML version of email body (optional)
        :return: True if successful, False otherwise
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = username
        msg['To'] = ', '.join(to_addrs) if isinstance(to_addrs, list) else to_addrs
        msg['Subject'] = subject

        # Attach both plain and HTML versions
        msg.attach(MIMEText(body, 'plain'))
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.sendmail(username, to_addrs, msg.as_string())
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def get_latest_notification(self, username: str, password: str, 
                                mailbox: str = 'INBOX', 
                                lookback: int = 1) -> List[Dict]:
        """
        Retrieve latest email notifications
        :param username: Your full email address
        :param password: Email account password/app-specific password
        :param mailbox: Mailbox to check (default: 'INBOX')
        :param lookback: Number of latest emails to retrieve
        :return: List of dictionaries with email details
        """
        emails = []
        try:
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(username, password)
                mail.select(mailbox)

                status, data = mail.search(None, 'ALL')
                if status != 'OK':
                    return []

                email_ids = data[0].split()
                latest_ids = email_ids[-lookback:]  # Get most recent emails

                for eid in latest_ids:
                    _, msg_data = mail.fetch(eid, '(RFC822)')
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Extract email details
                    email_info = {
                        'id': eid.decode(),
                        'from': msg['From'],
                        'to': msg['To'],
                        'subject': msg['Subject'],
                        'date': msg['Date'],
                        'body': self._extract_body(msg)
                    }
                    emails.append(email_info)
            return emails
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []

    def _extract_body(self, msg: email.message.Message) -> str:
        """Extract plain text body from email"""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    return part.get_payload(decode=True).decode()
        else:
            return msg.get_payload(decode=True).decode()
        return ""
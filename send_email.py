import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_via_smtp(to_email: str, subject: str, body_plain: str, body_html: str = None):
    """
    Sends email using smtplib + MIMEMultipart (works for both STARTTLS (587) and SSL (465)).
    """

    SMTP_SERVER       = "authsmtp.securemail.pro"
    SMTP_PORT         = 465
    SENDER_EMAIL      = "info@oposconia.com"
    SENDER_PASSWORD   = "IAoposiciones2025&"

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = to_email
    msg["Subject"] = subject

    # attach plain text
    msg.attach(MIMEText(body_plain, "plain"))
    # optionally attach HTML alternative
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    # connect
    if SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()

    try:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    finally:
        server.quit()
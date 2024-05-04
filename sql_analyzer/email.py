from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from sql_analyzer.config import mail


def send_email(subject, attach_filename, df):
    send_from = mail.sender_address
    password = mail.sender_password
    send_to = mail.receiver
    message = """\
    <p><strong>User request from chatbot&nbsp;</strong></p>
    <p><br></p>
    <p><strong>Greetings&nbsp;</strong><br><strong>DCiA Group 4 &nbsp;    </strong></p>
    """

    multipart = MIMEMultipart()
    multipart["From"] = send_from
    multipart["To"] = send_to
    multipart["Subject"] = subject
    attachment = MIMEApplication(df.to_csv())
    attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(f"{attach_filename}.csv")
    multipart.attach(attachment)
    multipart.attach(MIMEText(message, "html"))
    print(multipart["From"])
    print(password)
    # Use SMTP from gmail to send the email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    # server = smtplib.SMTP("smtp.163.com", 587)
    server.starttls()
    server.login(multipart["From"], password)
    server.sendmail(multipart["From"], multipart["To"], multipart.as_string())
    server.quit()

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from sql_analyzer.config import mail


def send_email(subject, attach_filename, user_email_address,user_message, df):
    send_from = mail.sender_address
    password = mail.sender_password
    send_to = mail.receiver

    # The content of the email
    message = f"""\
    <p><strong>User request from chatbot&nbsp;</strong></p>
    <p><br></p>
    <p>{user_message}</p>
    <p><br></p>
    <p>Please check the list of conversation and send the required data back to the following email address.</p>
    <p>{user_email_address}</p>
    <p><br></p>
    <p><strong>Greetings&nbsp;</strong><br><strong>DCiA Group 4 &nbsp;    </strong></p>
    """

    multipart = MIMEMultipart()
    multipart["From"] = send_from
    multipart["To"] = send_to
    multipart["Subject"] = subject

    # Transform df into csv and send it as an attachment
    attachment = MIMEApplication(df.to_csv())
    attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(f"{attach_filename}.csv")
    multipart.attach(attachment)
    multipart.attach(MIMEText(message, "html"))

    # Use SMTP from gmail to send the email
    result = True
    server = smtplib.SMTP("smtp.gmail.com", 587)
    try:
        server.starttls()
        server.login(multipart["From"], password)
        server.sendmail(multipart["From"], multipart["To"], multipart.as_string())
    except:
        result = False
    finally:
        server.quit()

    return result

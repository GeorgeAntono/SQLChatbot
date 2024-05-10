from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
from sql_analyzer.config import mail


def email_to_user(user_email_address, user_name, df):
    '''
    Email the user with data on request as an attachment.

    INPUT:
        user_email_address: str. the email address of the user
        user_name: str. the name of the user
        df: DataFrame. the dataframe containing the data to send to the user
    OUTPUT:
        bool. True if the email was sent, False otherwise.
    '''
    send_to = user_email_address

    subject = "Data from CDA Team on Request"

    # The content of the email
    message = f"""\
    <p>Hi {user_name},</p>
    <p><br></p>
    <p>Attached is the data you requested. Please review it.</p>
    <p><br></p>
    <p>Best regards,</p>
    <p>CDA Team, PostNL</p>
    """
    print(message)
    attach_filename = "data"

    return send_email(send_to, subject, message, df, attach_filename)

def email_to_analyst(user_email_address, user_message, df):
    '''
    Email the analyst team with conversation list as an attachment.

    INPUT:
        user_email_address: str. the email address of the user
        user_message: str. the message of the user
        df: DataFrame. the dataframe containing the conversation list
    OUTPUT:
        bool. True if the email was sent, False otherwise.
    '''
    send_to = mail.receiver

    subject = "Chatbot Customer Request"

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

    attach_filename = "Conversation_List"

    return send_email(send_to, subject, message, df, attach_filename)

def send_email(receiver, subject, message, df = None, attach_filename = None):
    '''
    The basic module to send email.

    INPUT:
        receiver: str. Email address of the receiver
        subject: str. Subject of the email
        message: str, in html. Body of the email
        df: DataFrame. Data to send as csv in attachment.
        attach_filename: str. Set the filename of the attachment of the email. Excluding '.csv'
    OUTPUT:
        bool. True if the email was sent, False otherwise.
    '''
    send_from = mail.sender_address
    password = mail.sender_password
    send_to = receiver

    multipart = MIMEMultipart()
    multipart["From"] = send_from
    multipart["To"] = send_to
    multipart["Subject"] = subject
    multipart.attach(MIMEText(message, "html"))

    # Transform df into csv and send it as an attachment
    if df is not None:
        attachment = MIMEApplication(df.to_csv())
        attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(f"{attach_filename}.csv")
        multipart.attach(attachment)

    # Use SMTP from gmail to send the email
    result = True
    server = smtplib.SMTP("smtp.gmail.com", 587)
    try:
        server.starttls()
        server.login(multipart["From"], password)
        server.sendmail(multipart["From"], multipart["To"], multipart.as_string())
    except Exception as e:
        print(str(e))
        result = False
    finally:
        server.quit()

    # server.starttls()
    # server.login(multipart["From"], password)
    # server.sendmail(multipart["From"], multipart["To"], multipart.as_string())
    # server.quit()

    return result

def validate_email(email):
    pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False
def mail_func(form, file_name):
    import smtplib
    import datetime

    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders


    now = datetime.datetime.now()

    email_user = 'id'
    email_password = 'password'
    email_send = form['recipient_email']
    subject = form['subject']

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = ", ".join(email_send)
    msg['Subject'] = subject

    body = 'Sent by ' + form['sender_name'] + '\n' + now.strftime("%Y-%m-%d %H:%M") + '\n' + form['body']
    msg.attach(MIMEText(body,'plain'))
    

    part = MIMEBase('application','octet-stream')
    part.set_payload(file_name)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= Document.pdf")

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)


    server.sendmail(email_user, email_send , text)
    server.quit()
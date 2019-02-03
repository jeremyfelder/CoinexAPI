from os.path import basename
import smtplib
from smtplib import SMTPException
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None, server="smtp.gmail.com"):
	assert isinstance(send_to, list)

	msg = MIMEMultipart()
	msg['From'] = send_from
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	for f in files or []:
		with open(f, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(f)
			)
		# After the file is closed
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)

	try:
		ssl_server = smtplib.SMTP_SSL(server, 465)
		ssl_server.login(send_from, "WebCrap^3LaCl")
		ssl_server.sendmail(send_from, send_to, msg.as_string())
		ssl_server.close()
	except SMTPException as e:
		print(e)
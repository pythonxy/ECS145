import urllib2, urllib
import sys
import subprocess, os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import tempfile
from threading import Thread
from HTMLParser import HTMLParser

class Parse(HTMLParser):
	def __init__(self):
		self.reset()
		self.fed = []
	def handle_data(self, d):
		self.fed.append(d)
	def get_data(self):
		return ''.join(self.fed)
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for atrName, atrValue in attrs:
				if atrName == 'href': self.fed.append(atrValue)

def grab_page():
	page = urllib2.urlopen('http://heather.cs.ucdavis.edu/~matloff/145/Blog.html')
	source = page.read()
	page.close()

	newFile = open('MatloffBlogNew.txt', mode='w')
	newFile.write(str(source))
	newFile.close()

def check_diff():
	diffOutput = subprocess.Popen(['diff MatloffBlogNew.txt MatloffBlogOld.txt'], /
		shell=True, stdout=subprocess.PIPE).stdout
	textDiff = tempfile.TemporaryFile()
	htmlDiff = tempfile.TemporaryFile()

	# copy in the diff, ignoring unwanted chars '< '
	firstLine = True
	for line in diffOutput:
		if firstLine:
			firstLine = False
		else:
			textDiff.write(line[2:])
			htmlDiff.write(line[2:])
	textDiff.seek(0)
	htmlDiff.seek(0)

	# parse out the html for the text version
	p = Parse()
	p.feed(textDiff.read())
	p.close()

	# if there was a diff
	if p.fed:
		subprocess.check_call("mv MatloffBlogNew.txt MatloffBlogOld.txt", shell=True)
		email_self(p.get_data(), '<html>' + htmlDiff.read() + '</html>')
	
	diffOutput.close()
	
def email_self(text, html):
	msg = MIMEMultipart('alternative')
	msg.attach(MIMEText(text, 'plain'))
	msg.attach(MIMEText(html, 'html'))
	msg["Subject"] = "145 BLOG UPDATE BIATCH!!!"
	msg["From"] = "ecsmailserver145@gmail.com"
	msg["To"] = "keyan.kousha@gmail.com"
	s = smtplib.SMTP("smtp.gmail.com", 587)
	s.ehlo()
	s.starttls()
	s.login("ecsmailserver145", "moneymoneymoney")
	s.sendmail("ecsmailserver145@gmail.com", ["keyan.kousha@gmail.com"], msg.as_string())
	s.quit()

def main():
	while True:	
		grab_page()
		check_diff()
		time.sleep(300)
	
main()
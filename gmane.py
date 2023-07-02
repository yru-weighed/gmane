import sqlite3
import time
import ssl
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urljoin
from urllib.parse import urlparse
import re
from datetime import datetime, timedelta

#Not all systems have this so conditionally define parser
try:
		import dateutil.parser as parser
except:
		pass

def parsemaildate(md) :
		#see if we have dateutil
		try:
				pdate = parser.parse(tdate)
				test_at = pdate.isoformat()
				return test_at
		except:
				pass
		
		#non-dateutil version- we try our berst

		pieces = md.split()
		notz = " ".join(pieces[:4]).strip()

		#try a bunch of format variations- strptime() is *lame*
		dnotz = None
		for form in [ '%d %b %Y %H:%M%S', '%d %b %Y %H:%M:%S',
	       '%d %b %Y %H:%M', '%d %b %Y %H:%M', '%d %b %y %H:%M:%S',
				 '%d %b %y %H:%M:%S', '%d %b %y %H:%M', '%d %b %y %H:%M' ] :
				try:
						dnotz = datetime.strptime(notz, form)
						break
				except:
						continue
		if dnotz is None:
				#print 'Bad Date:', md
				return None
		
		iso = dnotz.isoformat()

		tz = "+0000"
		try:
				tz = pieces[4]
				ival = int(tz) #only want numeric timezone values
				if tz == '-0000' : tz = '+0000'
				tzh = tz[:3]
				tzm = tz[3:]
				tz = tzh+":"+tzm
		except:
				pass
		
		return iso+tz

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('content.sqlite')
cur = conn.cursor()

#url of our API
baseurl = "http://mbox.dr-chuck.net/sakai.devel/"
#baseurl = "http://gmane.dr-chuck.net/gmane.comp.cms.sakai.devel/"
#when telling the url what messages we want, we specify it at the end...devel/1/2 will give messages 1-2
#...devel/101/102 will give messages 101 to 102

cur.execute('''CREATE TABLE IF NOT EXISTS Messages
		(id INTEGER UNIQUE, email TEXT, sent_at TEXT, 
		subject TEXT, headers TEXT, body TEXT)''')

#pick up where we left off
start = None
cur.execute('SELECT max(id) FROM Messages')
try:
		row = cur.fetchone()
		if row is None :
				start = 0
		else:
				start = row[0]
except:
		start = 0

if start is None : start = 0

many = 0
count = 0
fail = 0
while True:
		if (many < 1) :
				conn.commit()
				sval = input('How many messages: ')
				if ( len(sval) < 1 ) : break
				many = int(sval)

		start = start + 1
		cur.execute('SELECT id FROM Messages WHERE id=?', (start, ))
		try:
				row = cur.fetchone()
				if row is not None : continue	
		except:
				row = None

		many = many - 1
		url = baseurl + str(start) + '/' + str(start + 1)
		#take the base url, add the starting address and then +1 means after the / to indicate the pages you want retrieved

		text = "None"
		try:
				#open with a timeout of 30 seconds
				document = urllib.request.urlopen(url, None, 30, context=ctx)
				text = document.read().decode()
				if document.getcode() != 200 :			#making sure we get good data
						print("error code=", document.getcode(), url)
						break
		except KeyboardInterrupt:
				print('')
				print('Program interrupted by user..')
				break
		except Exception as e:
				print('Unable to retrieve or parse page', url)
				print('Error', e)
				fail = fail + 1
				if fail > 5 : break
				continue
		
		print(url, len(text))
		count = count + 1

		if not text.startswith('From ') :
				print(text)
				print('Did not find From ')
				fail = fail + 1
				if fail > 5 : break
				continue
		
		pos = text.find("\n\n")
		if pos > 0 :
				hdr = text[:pos]
				body = text[pos+2:]

		else:
				print(text)
				print('Could not find break between headers and body')
				fail = fail + 1
				if fail > 5 : break
				continue
		
		#finding an email address using regular expressions
		email = None
		x = re.findall('\nFrom: .* <(\S+@\S+)>\n', hdr)
		if len(x) == 1:
				email = x[0]
				email = email.strip().lower()
				email = email.replace("<", "")
		else:
				x = re.findall('\nFrom: (\S+@\S+)\n', hdr)
				if len(x) == 1 :
						email = x[0]
						email = email.strip().lower()
						email = email.replace("<", "")
		
		date = None
		y = re.findall('\Date: .*, (.*)\n', hdr)
		if len(y) == 1 :
				tdate = y[0]
				tdate = tdate[:26]
				try:
						sent_at = parsemaildate(tdate)
				except:
						print(text)
						print('Parse fail', tdate)
						fail = fail + 1
						if fail > 5: break
						continue
		
		subject = None
		z = re.findall('\Subject: (.*)\n', hdr)
		if len(z) == 1 : subject = z[0].strip().lower()

		#reset the fail counter
		fail = 0
		print("  ", email, sent_at, subject)
		cur.execute('''INSERT OR IGNORE INTO Messages (id, email, sent_at, subject, headers, body)
				VALUES (?, ?, ?, ?, ?, ?)''', (start, email, sent_at, subject, hdr, body))
		if count % 50 == 0 : conn.commit()		#every 50th email we are committing
		if count % 100 == 0 : time.sleep(1)		#every 100th we are waiting one second

conn.commit()
cur.close()
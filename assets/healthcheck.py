  #!/usr/bin/env python3
#
# Check the health of sensors making sure the files that should be there
# are there and that they are not stale. (modification time was greater than max_age
# seconds ago.
#
import os
import glob
import time
import sys

now = time.time()
maxAge = 180

error = []

errors_to = "nicci"
homepath = os.path.expanduser('~')
logfile = f'{homepath}/.local/logs/healthcheck.log'
efile = f'{homepath}/.healthcheck.errors'


def sendErrorEmail(subject,file):
	global errors_to
	mailcmd = f'/usr/bin/mail -s "{subject}" {errors_to} <{file} '
	os.system(mailcmd)
	

if os.path.exists(efile):
	sys.exit(1)

with open(logfile,"a") as log:
	tcnt = 0
	ecnt = 0
	with open(f'{homepath}/etc/hchecklist.txt') as f:
		files = f.read().strip().split('\n')
	for f in files:
		try:
			age = now - os.stat(f).st_mtime
			if age > maxAge:
				tcnt = tcnt + 1
				tmsg = f'{f}:{age} seconds'
				error.append(tmsg)
				print(tmsg,file=log)
			else:
				tfile = os.path.join(os.path.dirname(f),'time')
				if os.path.exists(tfile):
					try:
						addtl = ''
						then = int(open(tfile).read().strip())
					except:
						addtl = ':timestamp file did not have integer in it either.'
						then = int(os.stat(tfile).st_mtime);
					if (now - then) > maxAge:
						tmsg = f'{f}: timstamp file too old{addtl}'
						error.append(tmsg)
						print(tmsg,file=log)

		except Exception as e:
			ecnt = ecnt + 1
			emsg = f'Error {e} with {f}'
			error.append(emsg)
			print(f,emsg,file=log)

if len(error):
	with open(efile,'w') as f:
		f.write('\n'.join(error))
#		sendErrorEmail("Health Check Errors",efile)
else:
	if os.path.exists(efile):
		os.unlink(efile)

with open('/tmp/healthcheck.ran','w') as f:
	print('Ok',file=f)

sys.exit(tcnt+ecnt)


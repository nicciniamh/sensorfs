#!/usr/bin/env python3
#
# healthceck reads the file ~/etc/healthchecklist.txt, each line is a pathnamne to
# sensorfs sensor entity - each of these directories should have an entry called time.
# Since this is a consistent entry for any sensor it used to determine freshness of data.
#
# For each path in the list the file modification time is checked against current time
# and if the difference is greater than maxAge it is reported as stale. If the path
# doesn't exist or is unreadable it is reported as missing.
#
# When errors are found they are written to an error file ~/.healthcheckerrors.
# If there was no error file when healthcheck runs an email is sent to errora_to.
# If the file already existed, further emails aren't sent.
#
# If there are no errors and the error file exists (i.e., any errors are cleared)
# the error file is removed.

import os
import glob
import time
import sys

now = time.time()
maxAge = 180

error = []

errors_to = "phonenumber@cellprovider.tld"
logfile = "/home/user/.local/logs/healthcheck.log"
efile = f'/home/user/.healthcheck.errors'


def sendErrors(errors_to,error):
	mailcmd = f'/usr/bin/msmtp -f senhealth@ducksfeet.com {errors_to}'
	with os.popen(mailcmd,'w') as p:
		#print(f'Sending to {errors_to}: [{error}]')
		p.write(f'\n\n{error}\n')
	return True

with open(logfile,"a") as log:
	ecnt = 0
	now = time.time()
	with open('/home/user/etc/hchecklist.txt') as f:
		paths = f.read().strip().split('\n')
	for p in paths:
		sensor = os.path.basename(p)
		host = os.path.basename(os.path.dirname(p))
		sen = f'{host}/{sensor}'
		emsg = ''
		check = os.path.join(p,'time')
		if not os.path.exists(check):
			emsg = f'{sen}: missing'
			print(emsg,file=log)
			error.append(emsg)
			ecnt = ecnt + 1
			continue

		age = now - os.stat(check).st_mtime
		if age > maxAge:
			ecnt = ecnt + 1
			emsg = f'{sen}: stale data'
			error.append(emsg)

if len(error):
	errors = '\n'.join(error)
	error = f'{ecnt} error(s): {errors}'
	if not os.path.exists(efile):
		sendErrors(errors_to,error)
	with open(efile,'a') as f:
		f.write(error)
else:
	if os.path.exists(efile):
		os.unlink(efile)

with open('/tmp/healthcheck.ran','w') as f:
	print('Ok',file=f)

sys.exit(ecnt)


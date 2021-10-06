# Importing libraries
import imaplib
import re
import datetime as dt
from datetime import timedelta

dates = (dt.datetime.now() - timedelta(days = 1)).strftime("%d-%b-%Y")

user = 'varad.ahirwadkar368@gmail.com'
password = 'zglvbyahjkinjycs'
imap_url = 'imap.gmail.com'

# Function to get email content part i.e its body part
def get_body(msg):
	if msg.is_multipart():
		return get_body(msg.get_payload(0))
	else:
		return msg.get_payload(None, True)

# Function to search for a key value pair
# def search(key, value, con):
# 	result, data = con.search(None, key, '"{}"'.format(value))
# 	return data

def search(con):
	result, data = con.search(None, '(SENTSINCE {date})'.format(date=dates))
	return data


# Function to get the list of emails under this label
def get_emails(result_bytes):
	msgs = [] # all the email data are pushed inside an array
	for num in result_bytes[0].split():
		typ, data = con.fetch(num, '(RFC822)')
		msgs.append(data)

	return msgs
flag = True
con = imaplib.IMAP4_SSL(imap_url)
con.login(user, password)
con.select('INBOX')
#msgs = get_emails(search('FROM', 'varad.ahirwadkar368@gmail.com', con))
msgs = get_emails(search(con))

#print(msgs)


import sys
# sys.stdout = open('file', 'w')
# printing the body
for msg in msgs[::-1]:
    for body in msg:
        if type(body) is tuple:

            # encoding set as utf-8
            content = str(body[1], 'ISO 8859-1')
            data = str(content)

            # Handling errors related to unicodenecode
            try:
                indexstart = data.find("Subject:")
                data2 = data[indexstart + 9: len(data)]
                indexend = data2.find("From:")
                
                if re.search("advisories and nightlies", data2[0: indexend].strip()):
                    #print("outter: ",data2[0: indexend].strip())
                    indexstart = data.find("ltr")
                    clean_data = re.sub('<[^<]+?>', '', data[indexstart + 5: len(data)])

                    clean_data = re.split("--[0-9a-zA-Z]*--$" ,clean_data)
                    clean_data[0] = clean_data[0].strip()

                    clean_data[0] = clean_data[0].replace('=C2=A0', ' ').replace('=\r\n', '').replace(':-', '\n').replace("Nightlies", "- Nightlies:")
                    clean_data[0] = clean_data[0][:clean_data[0].find("JIRA")]
                    clean_data[0] = re.split("- ",clean_data[0])

                    for builds in clean_data[0]:
                        builds=builds.replace('=C2=A0', ' ')
                        # builds=builds.replace("Nightlies", "\n\n- Nightlies:")

                        if re.search(" image:", builds):
                            print(data2[0: indexend].strip())
                            print("\nAdvisories:")
                            print("image: ", builds[builds.find("image:"):].strip()) 
                        if re.search("rpm", builds):
                            print("rpm: ", builds[builds.find(":")+2:])
                        if re.search("extras", builds):
                            print("extras: ", builds[builds.find(":")+1:].strip())
                        if re.search("metadata:", builds):
                            print("metadata: ", builds[builds.find(":")+1:].strip()) 

                        if re.search("Nightlies:", builds):
                            print("\nNightlies:")
                        if re.search("ppc64le:", builds):
                            print("ppc64le: ", builds[builds.find("ppc64le:")+9:].strip()) # build
                            print("ppc64le: ", builds[builds.find("release-ppc64le:")+16:].strip())
                            build_no= re.search(":[0-9.]+",builds[builds.find("ppc64le:")+9:].strip())
                            
                            if build_no is not None:
                                print("build no: ", build_no.group()[1:])
                                with open("build_no.sh","w") as f:
                                    f.write("#!/bin/bash\nexport NIGHTLY_Z_VARAD="+build_no.group()[1:]+"\n")
                                    f.close()
                                #print("export NIGHTLY_Z_VARAD=%s" % (pipes.quote(str(build_no.group()[1:]))))
                        if re.search("s390x:", builds):
                            print("s390x: ", builds[builds.find(":")+1:].strip()) 
                        if re.search("x86_64:", builds):
                            print("x86_64: ", builds[builds.find(":")+1:].strip()) 
                            flag=False
                            print("\n================================================================================================")
                            break
                        #print(builds)
         
                   
            except UnicodeEncodeError as e:
                pass

        if flag == False:
            break   
    if flag == False:
            break  
# sys.stdout.close()

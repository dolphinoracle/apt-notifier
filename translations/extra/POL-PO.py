#!/usr/bin/python3

import glob, os
import xml.etree.ElementTree as ET

policies = """
	../policy/org.mxlinux.apt-notifier.auto-update-disable.policy
	../policy/org.mxlinux.apt-notifier.auto-update-enable.policy

    """

for po in glob.glob("*.pol"):
	os.remove(po)

for po in glob.glob("EN.POL"):
	os.remove(po)

for pol in policies.split():
	print("#---------------------")
	print("policy: " + pol)
	print("#---------------------")
	with open(pol, 'r') as file:
		xml = file.read().replace('xml:lang=','lang=')
	
	policy = ET.fromstring(xml)
	
	for msg in policy.iter('message'):
		if  msg.get('lang') is None:
			en_text = msg.text
			with open('EN.POL','a') as file:
				file.write(f'\nmsgid "{en_text}"\n')
				file.write('msgstr ""\n')
			break
	
	for msg in policy.iter('message'):
		lang = msg.get('lang')
		text = msg.text
		if msg.get('lang') is None:
			continue
		if en_text in text:
			continue
		print(lang, text)
		with open(lang + '.pol','a') as file:
			file.write(f'\nmsgid "{en_text}"\n')
			file.write(f'msgstr "{text}"\n')

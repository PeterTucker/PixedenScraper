
from bs4 import BeautifulSoup # sudo easy_install BeautifulSoup4
import time
import requests # sudo easy_install pip, pip install requests
import urllib
import os
import re
import cgi

import mechanize # sudo easy_install mechanize
import cookielib

from selenium import webdriver # sudo easy_install selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains


# Define colors for print out
class bcolors:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	END = '\033[0m'


def printer(str, color, ends = False):
	if ends:
		print color + "---------- " + str + " ----------" + bcolors.END
	else:
		print color + str + bcolors.END

# Main Function
def scrapper():
	global _dir
	global start_i
	global end_i
	global base_url
	global sub_url
	global br
	global cj

	printer('STARTING SCRAPPER', bcolors.GREEN,  True);
	printer('Downloading to: '+_dir, bcolors.GREEN,  False);

	index = start_i

	while index < end_i + 1:
		page_url = sub_url + 'Page-' + str(index);

		if index == 1:
			page_url = 'http://www.pixeden.com/web-design-templates/'
			
		printer('Starting Page: ' + page_url, bcolors.GREEN,  False);
		
		page_soup = BeautifulSoup(requests.get(page_url).text) # Grab Source from Page

		item_divs = page_soup.findAll("div", { "class" : "itemContainer" })
		for item in item_divs:
			item_url = base_url + item.find('a')['href']
			print '\n'
			printer('Downloading Asset: ' + item_url, bcolors.YELLOW, True)

			try:
				resp = br.open(item_url);
				item_soup = BeautifulSoup(resp.read())
				download_div = item_soup.findAll("div",{"id": "download"})
				download_url = base_url + download_div[0].find('a')['href']
				print "download: " + download_url

				f = urllib.urlopen(download_url)
				
				try:
					_, params = cgi.parse_header(f.headers.get('Content-Disposition', ''))
					zip_name = params['filename']
				except Exception:
					zip_name = item.find('a')['href'].split('/')[2] + '.zip'

				with open(zip_name, "wb") as PSD:
					PSD.write(f.read()) # Save our File

				printer('Finished Downloading: ' + zip_name, bcolors.GREEN, True)
				sleep(5)

			except Exception, e:
				print e
				printer('Error Downloading: ' + item_url, bcolors.RED, True)
				print download_div
				
			print '\n'
		index+=1

	printer('SCRAPPER HAS FINISHED', bcolors.GREEN,  True);
	second_try()


def second_try(): # have to still implement
	global failed_downloads

# End Index
def get_end(_end):
	global source_soup
	_max = 1
	line = source_soup.find('li', {"class":"pagination-end"})
	a = line.find('a')
	_max = int(re.findall(r'\d+',  a['href'])[0])
	
	if(_end <= 0):
		return _max

	if(_end>=_max):
		return _max
	else:
		return _end


# Define our Globals
global _dir
global base_url
global start_i # Start Page Index
global end_i # End Page Index
global source_code
global source_soup

# Directory Setup
_dir = os.path.dirname(os.path.realpath(__file__)) + '/dump/'
if not os.path.exists(_dir):# Make our Initial Directory Comic Dump
	os.makedirs(_dir)
os.chdir(_dir)

# Define Inital URLs
base_url = 'http://www.pixeden.com';
sub_url = base_url+'/latest/';
# /free-web-design-templates/
# /web-design-templates/
# /print-graphic-design-templates

# Get our HTML to scrape and create a Soup Object
source_code = requests.get(sub_url)
source_soup = BeautifulSoup(source_code.text)

# Define Inital Variables
start_i = 1
end_i = get_end(-1)

# Login to PixeDen.com
global br 
global cj 
br = mechanize.Browser()
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
username = '*******'
password = '*******'
br.set_handle_equiv(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [('User-agent', 'Chrome')]
br.open(base_url)
formcount=0
for frm in br.forms():  
  if str(frm.attrs["id"])=="form-login":
    break
  formcount=formcount+1
br.select_form(nr=formcount)
br.form['username'] = username
br.form['passwd'] = password
br.submit()



# Check if we're logged in
if(br.response().read().find(username) != -1): # Logged In
	printer("Logged in as " + username, bcolors.GREEN, True)
	
	# Execute Scrapper
	scrapper()
else:# Could not log in
	printer("Oh No! You could not be logged in!", bcolors.RED, True)

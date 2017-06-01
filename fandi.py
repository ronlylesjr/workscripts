from splinter import Browser
import pickle
import time
from selenium.webdriver.common.keys import Keys

fileObject = open('creds','rb') 
creds = pickle.load(fileObject)

MFGR = '<script type="text/javascript" src="MFGRexample.js"></script>'
nonMFGR='<script type="text/javascript" src="nonMFGRexample.js"></script>'

livelogin = 'https://admin.ebizautos.com/'
sboxlogin = 'https://admin.sandbox.ebizautos.com/'
livesearch = 'https://admin.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
sboxsearch = 'https://admin.sandbox.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
livecp = 'https://cp.ebizautos.com/index.cfm?ebxid=314'
sboxcp = 'https://cp.sandbox.bizautos.com/index.cfm?ebxid=314'
browser = Browser()

aids = {'####' : 'DealerName'
}

browser.visit(livelogin)
browser.fill('username', list(creds.keys())[0])
browser.fill('Password', creds[list(creds.keys())[0]))
browser.find_by_xpath('/html/body/div[1]/div/div[1]/form/table/tbody/tr[6]/td/div[1]/a').click()
time.sleep(2)

for aid in aids.items():
	browser.visit(livesearch + aid[0])
	browser.find_by_xpath('/html/body/div[7]/div[2]/div[3]/div[1]/div[2]/form/div[1]/input[2]').click()
	if not browser.is_element_not_present_by_xpath('/html/body/div[7]/div[2]/div[1]/div[10]/div[1]/div[4]/div/form/input[1]', wait_time=3):
		browser.find_by_xpath('/html/body/div[7]/div[2]/div[1]/div[10]/div[1]/div[4]/div/form/input[1]').click()
	time.sleep(2)
	browser.visit(livecp)
	browser.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL, 'w')
	time.sleep(1)
	# browser.find_by_css('html body div#BodyContainerWide div#MainBody.ClearFix div#BodyContent form#form div#SettingsFrameworkTemplate table.TextStyle tbody tr td a#AddTopLevelPage.TextSettings strong u').first.click()
	print('\a Click Sub page and hit Enter...')
	pause = input()
	browser.find_by_css('html body div#BodyContainerWide div#MainBody.ClearFix div#BodyContent form#form div#SettingsFrameworkTemplate div#AddPagePopup div select#PageTypes')
	browser.select('PageTypes', '13')
	browser.find_by_css('html body div#BodyContainerWide div#MainBody.ClearFix div#BodyContent form#form div#SettingsFrameworkTemplate div#AddPagePopup div input#AddPageName.inputbox').fill('Finance & Insurance')
	browser.find_by_css('html body div#BodyContainerWide div#MainBody.ClearFix div#BodyContent form#form div#SettingsFrameworkTemplate div#AddPagePopup div center div#AddPageLevelButton').click()
	print('\aPlease make page live, select new page, and hit Enter to continue...')
	pholder = input()
	browser.find_by_xpath('/html/body/div[8]/div/div/form/div/div[9]/div[1]/a').click()
	time.sleep(2)
	if 'MFGR' in aid[1]:
		browser.find_by_xpath('/html/body/div[8]/div/div/form/div/div[9]/textarea').fill(MFGR)
	else:
		browser.find_by_xpath('/html/body/div[8]/div/div/form/div/div[9]/textarea').fill(nonMFGR)
	browser.fill('PageTitle', '')
	browser.find_by_xpath('/html/body/div[8]/div/div/form/div/div[10]/ul/li/a').click()

browser.quit()

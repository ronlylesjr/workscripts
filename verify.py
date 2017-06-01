from splinter import Browser
import pickle
import time
from selenium.webdriver.common.keys import Keys

fileObject = open('creds','rb') 
creds = pickle.load(fileObject)


livelogin = 'https://admin.ebizautos.com/'
sboxlogin = 'https://admin.sandbox.ebizautos.com/'
livesearch = 'https://admin.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
sboxsearch = 'https://admin.sandbox.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
livecp = 'https://cp.ebizautos.com/index.cfm?ebxid=314'
sboxcp = 'https://cp.sandbox.bizautos.com/index.cfm?ebxid=314'
browser = Browser()

aids = [8820,10973,8523,8458,12136,8868,8858,8119,11445,8465,1769,8439,8857,11596]

browser.visit(livelogin)
browser.fill('username', list(creds.keys())[0])
browser.fill('Password', creds[list(creds.keys())[0]])
browser.find_by_xpath('/html/body/div[1]/div/div[1]/form/table/tbody/tr[6]/td/div[1]/a').click()
time.sleep(2)

for aid in aids:
	browser.visit(livesearch + str(aid))
	browser.find_by_css('html body#MainAdminBody div#BodyContainerWide div#MainBody.ClearFix div#LeftNav div.Content div div.Nav3 a').click()
	
	browser.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL, '1')
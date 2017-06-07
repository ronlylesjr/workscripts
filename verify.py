from selenium.webdriver.common.keys import Keys
from splinter import Browser
import getpass
import time

def main(aids):
	livelogin = 'https://admin.ebizautos.com/'
	sboxlogin = 'https://admin.sandbox.ebizautos.com/'
	livesearch = 'https://admin.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
	sboxsearch = 'https://admin.sandbox.ebizautos.com/index.cfm?section=accounts&page=manage&settings=overview&aid='
	livecp = 'https://cp.ebizautos.com/index.cfm?ebxid=314'
	sboxcp = 'https://cp.sandbox.bizautos.com/index.cfm?ebxid=314'
	login = False

	while login == False:
		username = input('Username: ')
		password = getpass.getpass('Password: ')
		browser = Browser()
		browser.visit(livelogin)
		browser.fill('username', username)
		browser.fill('Password', password)
		try:
			browser.find_by_xpath('/html/body/div[1]/div/div[1]/form/table/tbody/tr[6]/td/div[1]/a').click()
			time.sleep(2)
			for aid in aids:
				browser.visit(livesearch + str(aid))
				browser.find_by_css('html body#MainAdminBody div#BodyContainerWide div#MainBody.ClearFix div#LeftNav div.Content div div.Nav3 a').click()
				browser.driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL, '1')
			login = True
		except:
			print('Login error\a')
			browser.quit()

if __name__ == '__main__':
	aids = [9433,5766,9387,8464,8482,8966,10158,10209,12487,761,835,8479,8485]
	main(aids)

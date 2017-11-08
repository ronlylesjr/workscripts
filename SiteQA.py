from bs4 import BeautifulSoup
from splinter import Browser
import datetime
import pandas as pd
import re
import requests
import time


today = datetime.datetime.now()


def findPageType(soup):

    script = soup.find('script', attrs={'language' : 'javascript'})
    pattern = re.compile("(\w+): (.*)")
    fields = dict(re.findall(pattern, script.text))
    pagetype = fields['PageType']
    return pagetype 


def dictValue(field, present=False):
    '''Determines test value of a field based on the name'''


    refdict = {
                '1234567890' : ['Phone', 'Num', 'Amount', 'Zip'], 
                'test.me@ebizautos.com' : ['Email'], 
                today.strftime('%m/%d/%Y') : ['Date'], 
                '01/01/1985' : ['DateOfBirth']
                }

    while present == False:
        for item in refdict.items():
            if any (x in field for x in item[1]):
                value = item[0]
                present = True
            if not present:
                value = 'Test'
                present = True
    return value


def dictBuilder(appurl):        
    '''Build dictionary based on the required items on the form.'''


    soup = BeautifulSoup((requests.get(appurl)).text, 'lxml')
    fields = (x.get('id') for x in soup.findAll('input') if x.has_attr('required'))
    appDict = {x : dictValue(x) for x in fields}
    return(appDict)    


def PageResults(soup):              
    '''Takes url and determines status of page as either 
    (Responsive/Not Responsive) and checks if link is broken or leads to 404'''


    try:
        if (soup.find('div', attrs={'id' : 'side-panel'})):
           respfinding = 'Responsive'
        else:
            respfinding = 'Not Responsive'
        if (soup.find('div', attrs={'class' : 'error404'})):
           errorfinding = '404'
        else:
            errorfinding = 'OK'         
    except:
       respfinding = 'Broken Link'
       errorfinding = 'Broken Link'
    try:
        pagetype = findPageType(soup)
    except:
        pagetype = 'N/A'
    return (respfinding, errorfinding, pagetype)   


def geturls(soup, FinURL):          
    '''Finds link for Request More Info form and Credit app.
    Grabs first inventory link from sitemap and goes to that
    vehicle for the link for the Request More Info link'''


    links = ('http:' + x.get('href') if x.get('href')[:1] == '/' else x.get('href')
            for x in soup.findAll('div', 
            attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'})[1].findAll('a') 
            if x.has_attr('href'))
    
    ExampleCar = next(links)                                                             
    srp = BeautifulSoup((requests.get(ExampleCar)).text, 'lxml')
    RMI = srp.find('a', attrs={'id' : 'srp-vehicle-request-more-info'})          
    form = RMI.get('data-source')
    FinPage = BeautifulSoup((requests.get(FinURL)).text, 'lxml')
    FinURL = FinPage.find('a', attrs={'class' : 'button button-large'})                   
    appurl = FinURL.get('href')                                                         
    return(form, appurl)


def filloutleads(contacturl, appurl):       
    '''Fills out lead forms specified in geturls()'''
    #TODO: see if we can get addendumDict inside appDict.


    formDict = dictBuilder(contacturl)      
    appDict = dictBuilder(appurl)
    addendumDict = {
                    'ctlTypedSignature' : 'test', 
                    'ctlDateSigned' : today.strftime('%m/%d/%Y')
                    } 
    browser = Browser()
    browser.visit(contacturl)
    browser.fill_form(formDict)    
    browser.find_by_text('Send').click()
    browser.visit(appurl)

    try:
        browser.fill_form(appDict)
    except:
        # print('Failed to fill out credit app')
        pass
    page = requests.get(appurl)
    soup = BeautifulSoup(page.text, 'lxml')    

    for menu in soup.findAll('select'):
        if menu.has_attr('required'):            
            if 'CoApplicant' in str(menu.get('id')):
                pass
            elif 'State' in str(menu.get('id')):
                browser.select(menu.get('name'), 'AL')
            elif 'Years' in str(menu.get('id')):
                browser.select(menu.get('name'), '1')
            elif 'Month' in str(menu.get('id')):
                browser.select(menu.get('name'), '1')

    browser.fill_form(addendumDict)
    browser.find_by_xpath('''/html/body/section/form/div/fieldset[7]/div[1]/div[4]/div/div/div/label/span''').click()
    browser.find_by_text('Submit Your Application').click()
    browser.quit()

      
def build_report(url):            
    linksummary = {}
    sitemap = url + 'sitemap.aspx'
    s = requests.Session()
    s.get(url)
    mapsoup = BeautifulSoup((s.get(sitemap)).text, 'lxml')
    script = mapsoup.find('script', attrs={'language' : 'javascript'})
    pattern = re.compile("(\w+): '(.*?)'")
    fields = dict(re.findall(pattern, script.text))
    Summarytitle = fields['DealerName'] + ' Summary.csv'
    print(fields['DealerName'])
    
    titles = [link.text for link in mapsoup.find('div',
            attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'}).findAll('a') 
            if link.has_attr('href')]

    links = ['http:' + link.get('href') if link.get('href')[:1] == '/' else  
            link.get('href') for link in mapsoup.find('div', 
            attrs={'class' : 'col-xs-12 col-sm-6 col-md-4'}).findAll('a') 
            if link.has_attr('href')]

    comboresults = [PageResults(BeautifulSoup((s.get(x)).text, 'lxml')) 
                    if x[0:(len(url))] == str(url) else 
                    ('Different Domain', 'Different Domain', 'N/A')
                     for x in links]

    financeref = (comboresults.index(x) for x in comboresults 
                    if str(x[2])[:1] == '3')
    
    try: 
        FinURL = links[next(financeref)]
    except: 
        print('Could not find Finance Page') 

    #Breaks down tuple from PageResults() and puts values in lists
    respresults = [x[0] for x in comboresults]          
    errors = [x[1] for x in comboresults]        

    #Build pandas DataFrame
    linksummary['Title'] = titles                   
    linksummary['Link'] = links
    linksummary['Is_Responsive'] = respresults
    linksummary['Errors'] = errors    
    df = pd.DataFrame(linksummary)
    df = df[['Title', 'Link', 'Is_Responsive', 'Errors']]
    df.to_csv('QA Summaries/' + Summarytitle)

    if df['Is_Responsive'].isin(['Not Responsive']).any() == True or df['Errors'].isin(['404']).any() == True:
        print('\aPlease check summary to see errors') 

    #Browser automation
    try:             
        theurls = geturls(mapsoup, FinURL)
        print('Starting browser automation...')
        filloutleads(theurls[0], theurls[1])                
    except: 
        print('Could not find RMI/Credit app link')


if __name__ == '__main__':
    url = input('Please paste URL: \n')
    build_report(url)

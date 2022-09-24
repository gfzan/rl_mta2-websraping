# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 20:42:09 2022

@author: gfzan
"""
# import libraries #
import time
import timeit
from bs4 import BeautifulSoup

## need selenium to load the page for HTML to show
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
#import bamboolib as bam

#initiate the driver
#driver = webdriver.Chrome("DRIVER/chromedriver")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

#webdriver.Chrome(self.PATH)
#self.PATH = "DRIVER/chromedriver"



##### FIRST CLASS
startUrl = 'https://www.google.com/maps/search/ASST+Lombardia/@45.7388979,8.7637112,9z/data=!3m1!4b1'

class AsstUrlRetrieve:
    
# =============================================================================
#     self.places = [] 
#     self.addresses = []
#     self.categories = []
#     self.ratings = []
#     self.webSite = []
# =============================================================================
    
    def __init__(self, driver=driver, url = startUrl):
        #self.PATH = "DRIVER/chromedriver"
        self.driver = driver 
        self.url = url
        
    
    def getAsstUrl(self):
        self.driver.get(self.url)
        time.sleep(3)
        
        # Clicking on initial button :
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Rifiuta tutto']"))).click()
        except:
            pass

        time.sleep(4)
        start = timeit.default_timer()

        # identify scrolling element first i.e. the sidebar
        
        scrolling_element_xpath = '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]'
        scrolling_element= self.driver.find_element(By.XPATH, scrolling_element_xpath)    
        
        # use height of element to determine if need to scroll 
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrolling_element)
        print('last height = ', last_height)
        
        SCROLL_PAUSE_TIME = 2.0 # pause before next scroll, to let page load 
        t = 0 # number of times we have scrolled
        
        ## Loop the scrolling until cannot scroll anymore
        while True:
            print('time is = ', t)
            # Scroll down to bottom of whatever is currently loaded
            self.driver.execute_script('arguments[0].scrollTo(0, arguments[0].scrollHeight)', scrolling_element)
            t = t+1
        
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
        
            # Check if more scrolling required 
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrolling_element)
            print(new_height)
            if new_height == last_height:
                break
            last_height = new_height
        
        stop = timeit.default_timer()
        print('Time taken: ', stop - start)
        ## get the page HTML, inspect the code to find appropriate selector
        inq_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        ## select each of the saved locations
        ## selector is taken by clicking 'copy selector' in inspect
        
        selector = "#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div.m6QErb.DxyBCb.kA9KIf.dS8AEf.ecceSd > div"
        items = inq_soup.select(selector)
        
        ## every other 'div' element in 'items' is not actually a saved location! So let's drop these. 
        items_cleaned = items[::2]
        print(len(items_cleaned))
        ## a number like 66 (check that it is the same length as your saved list)
        
        ## test one item to see what information can be extracted
        #print(items_cleaned[1].prettify())
        return items_cleaned
    
    
    def linkWaitingTime(self, items_cleaned):
        places,addresses,categories,ratings,webSite = [],[],[],[],[]

        for i in items_cleaned:
            ## places
            selector_places = "div.UaQhfb span"
            try:        
                places.append(i.select_one(selector_places).text) 
            except:
                places.append(i.select_one(selector_places)) 
        
            ## ratings
            #selector_ratings = 'span.section-result-rating > span'
            selector_ratings = 'span.MW4etd'
            try:
                ratings.append(i.select_one(selector_ratings).text) 
            except:
                ratings.append(i.select_one(selector_ratings))
        
            ## category 
            selector_category = 'span[jsinstance="0"] span[jstcache="135"]'
            try:
                categories.append(i.select_one(selector_category).text)
            except:
                categories.append(i.select_one(selector_category))
            
        
            ## address
            selector_address = 'span[jsinstance="*1"] span[jstcache="135"]'
            try:
                addresses.append(i.select_one(selector_address).text)
            except:
                addresses.append(i.select_one(selector_address))
                            
        
            ##WEB SITE
            selector_web = 'div.etWJQ > a'
            try:
                webSite.append((i.select_one(selector_web)).get('href'))
                #print((i.select_one(selector_web)).get('href'))        ## PRINT URL
            except:
                webSite.append('null')
            #print('WEBSITE IS ::: =  ', webSite)
            
                    
            data = {'Place': places,
                    'Address': addresses,
                    'Category': categories,
                    'Rating': ratings,
                    'Web Site': webSite}
        
        ## sanity check on the length 
        print(len(places), len(ratings), len(categories), len(addresses))
        return data
    
    def saveData(self, data):       
            
        df = pd.DataFrame(data)
        df.head()
           
        # Step: Drop rows where (Web Site is one of: null) or (Web Site is missing)
        df = df.loc[~((df['Web Site'].isin(['null'])) | (df['Web Site'].isna()))]
        
        # Step: Drop duplicates based on ['Web Site']
        df2 = df.drop_duplicates(subset=['Web Site'], keep='first')
        
        writer = pd.ExcelWriter('XLS/asst_links.xlsx', engine='openpyxl')
        df2.to_excel(writer, sheet_name='asst_data')
        writer.save()



##### SECOND CLASS
class AsstGoogleMapScraper:

    def __init__(self, driver=driver):
        #self.PATH = "DRIVER/chromedriver"
        self.driver = driver 
        self.asst_list = []
        self.asst_info = {}
        self.asst_info["title"] = "NA"
        self.asst_info["website"] = "NA"

        self.STRING = ["//a[contains(translate(@*,'TRASPARENTE', 'trasparente'),'trasparente') or contains(translate(.,'TRASPARENTE', 'trasparente'),'trasparente')] \
                | //a[contains(translate(./img/@alt,'TRASPARENTE', 'trasparente'),'trasparente')]", \
                "//a[contains(translate(text(),'SERVIZIOGAT', 'serviziogat'),'servizi erogati')] | //a[contains(translate(./*/.,'SERVIZIOGAT', 'serviziogat'),'servizi erogati')]", \
                 "//a[contains(translate(.,'ATES','ates'),'attesa')]", \
                "//a[contains(translate(.,'ATES','ates'),'attesa')]"]
        
    ########## function 1 LOAD DATA
    def loadData(self, pathXlsFile, sheet):
        ## import data
        links = pd.read_excel(pathXlsFile, sheet)
        self.list_links = [x for x in links['Web Site'] if type(x) is str]
        #self.list_links = [self.list_links[x] for x  in (0, 6, 14)]
        return self.list_links
        print(len(self.list_links))

    ########## function 2 
    def searchElems(self, string):
        self.newLinks = []
        links=[x.get_attribute("href") for x in self.driver.find_elements(By.XPATH,string)]
        ### elimino i duplicati dalla lista ########
        if isinstance(links, list):
            links = list(dict.fromkeys(links))
        ############################################

        ## parso i tag a conteneti "trasparente"
        for i in links:
            self.driver.get(i)
            try:
                stringH = [x.text for x in self.driver.find_elements(By.XPATH,"//h1 | //h2 | //h3")]    ## restituisce  TYPE LIST
                for ii in stringH:
                    if 'attesa' in ii.lower():
                        print(f'WEBSITE IS  {i}')
                        return {'web_site': str(i)}
            except:
                pass
        return links

    ########## function 3
    def iterFunct(self, results, count=2, countString=1):
        count = count
        countString = countString

        for i in results:
            try:
                string=self.STRING[countString]
                self.driver.get(i)
                time.sleep(3)
                newResults = self.searchElems(string)
                ### elimino i duplicati dalla lista ########
                if isinstance(newResults, list):
                    newResults = list(dict.fromkeys(newResults))
                ############################################
                print(f'{count}- type is :  {type(newResults)} ')
                print(f'{count}-  {type(newResults)}   :   {newResults}')
                print(f'{count}-  la stringa usata è  :   {string}')

                if isinstance(newResults, str) or newResults is None:
                    self.asst_info["website"] = newResults
                    return
                elif isinstance(newResults, dict):
                    self.asst_info["website"] = newResults["web_site"]
                    return
                elif len(newResults)==1 and 'attesa' in newResults[0]:
                    self.asst_info["website"] = newResults
                    return
                else:
                    count +=1
                    countString +=1
                    self.iterFunct(newResults, count, countString)
            except:
                print('nothing to do')

    ########## MAIN function
    def get_asst_info(self, url):

        self.driver.get(url)
        print(' ')                                                        ## DEBUG
        print("#####################################################")    ## DEBUG
        print('carico url da elenco file XLS =   ', url)                  ## DEBUG
        time.sleep(3)

        # Clicking on initial button :
        try:
            WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Rifiuta tutto']"))).click()
        except:
            pass
        time.sleep(2)

         # Parse data out of the page
        self.asst_info["title"] = self.driver.title

        self.asst_info["website"] = 'NO website'

        ###  CASE 0
        string = self.STRING[0]
        results = self.searchElems(string)
        print('1- type is :   ', type(results))
        print('1- ',type(results), '  :   ', results)
        if isinstance(results, str) or results is None:
            self.asst_info["website"] = results
        elif isinstance(results, dict):
            self.asst_info["website"] = results["web_site"]

        ### OTHERS CASES
        else:
            self.iterFunct(results)

        self.asst_list.append(self.asst_info.copy())
        return self.asst_list
    
    ########## function 4 SAVE DATA
    def saveData(self, asst_list):
        df = pd.DataFrame.from_dict(asst_list)
        # Step: Drop rows where website is: NO website
        df2 = df.loc[~(df['website'].isin(['NO website']))]

        # Step: Drop duplicates based on ['website']
        df2['website'] = df2['website'].astype('string')
        df2 = df2.drop_duplicates(subset=['website'], keep='first')

        writer = pd.ExcelWriter('XLS/asst_links.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace')
        df2.to_excel(writer, sheet_name='listeAttesa_links3_spyder')
        writer.save()
        
        
if __name__ == "__main__":
    ########## 1 CLASS
    asstRetrieve = AsstUrlRetrieve()
    items_cleaned = asstRetrieve.getAsstUrl()
    data = asstRetrieve.linkWaitingTime(items_cleaned)
    asstRetrieve.saveData(data)
    
    
    
    ########## 2 CLASS
    asstScraper = AsstGoogleMapScraper()
    urls = asstScraper.loadData('XLS/asst_links.xlsx','asst_data')

    for url in urls:
        asst_list = asstScraper.get_asst_info(url)
        print(asstScraper.asst_info)
    #print(asstScraper.asst_list)

    asstScraper.saveData(asst_list)
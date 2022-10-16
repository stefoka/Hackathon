
import time
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver


#Function deletes cache of chromedriver when the browser is stuck
def delete_cache():
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3) # send right combination
    actions.perform()
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 4 + Keys.ENTER) # confirm
    actions.perform()
    time.sleep(5) # wait some time to finish
    if(len(driver.window_handles)>1):
        driver.close() # close this tab
        driver.switch_to.window(driver.window_handles[0]) # switch back


#These are not necessary
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36']

#Here we set the Load Srategy to eager so that we can go through the html pages without having to wait for the full loading
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"



#Different option which should make the browser faster.
options = Options()
options.add_argument('--window-size=1920,1820')
options.add_argument(
    'user-agent=' + 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')  # '#user_agents[(randint(0, 2))])
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-gpu')
options.add_argument('--headless')
options.add_argument('--disable-application-cache')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("disable-infobars")
options.add_argument('--no-sandbox')


##The path to chromedriver.exe is specified here. Can be added to a separate property file
driver = webdriver.Chrome(desired_capabilities=caps, executable_path='C:/Out2Bound/Latest Leadgen-Scraper/Leadgen-Scraper/chromedriver.exe',
                          options=options, )
#Always maximize windows so that all html elements are visible
driver.maximize_window()


#Here we define the url to the page which holds a list of job offers. Can be added to the separate property file
#driver.get('https://www.jobs.bg/front_job_search.php?subm=1&categories%5B%5D=29&location_sid=1&id=5&submit_vote=true&query_string=%7B%22categories%22%3A%5B%2229%22%5D%2C%22location_sid%22%3A%224%22%7D&is_it=0')
driver.get('https://www.jobs.bg/front_job_search.php?subm=1&is_entry_level=1&position_level%5B%5D=9&id=2&submit_vote=true&query_string=%7B%22position_level%22%3A%5B%229%22%5D%7D&is_it=0')
driver.set_page_load_timeout(5)

#Here we define the object which will be converted to a csv file.

obj = {}
url = []
title = []
description = []
company =[]
location = []
work = []
schedule = []
school = []
experience = []
urls = []

#We waith for the html of the list to be present in the page
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="listColumnsWrapper"]')))

#We define the jobs_url, which will contain the urls to the job offers and also one variables which will play a role in the logic for scrolling.
#We need to scroll to the bottom of the page in order to get all of the job offer urls, but we need to know when to stop scrolling
jobs_url = []
compare_jobs_url = -1
time.sleep(5)


while WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//li[contains(@additional-params, "list_datetime")]'))) and len(

    jobs_url) > compare_jobs_url:

    jobs_url = list(dict.fromkeys(jobs_url))
    compare_jobs_url = len(jobs_url)

    li_elements = driver.find_elements(By.XPATH, '//li[contains(@additional-params, "list_datetime")]')

    for elem in li_elements:
        url_href = elem.find_element(By.CSS_SELECTOR, 'a[class="black-link-b"]').get_attribute('href')
        #With this method we add a lot of duplicates in the urls array so we need to make sure there are no duplicates
        if(url_href not in urls):
            urls.append(elem.find_element(By.CSS_SELECTOR, 'a[class="black-link-b"]').get_attribute('href'))
            #We also get the namer of the company from the list as it is easire then doing it from the form view.
            company.append(elem.find_element(By.CSS_SELECTOR, 'a[class="black-link-b"]').get_attribute('href') + ',' + elem.find_element(By.CSS_SELECTOR, 'div[class="secondary-text"]').text)
        jobs_url.append(elem.find_element(By.XPATH, '//a[contains(@href, "https://www.jobs.bg/job/")]'))
        # title.

    jobs_url = list(dict.fromkeys(jobs_url))
    #company = list(dict.fromkeys(company))

    print('Urls taken so far:  ' + str(len(urls)))


    #Scrolling logic
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(1)
    if (compare_jobs_url == len(jobs_url)):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1)
    #print(len(urls))




################################################################
company = list(dict.fromkeys(company))
urls = list(dict.fromkeys(urls))
print('Total URLS:  ' + str(len(urls)))
company = [c.split(',', 1)[1] for c in company]
time.sleep(10)
num = -1
delete_cache()
new_company_arr=[]
#Here we enter the form view of every job offer and we take all of the necessary values.
for i in urls:
    num = num + 1
    if(num%100==0):
        #Prints a message every 100 records
        print ("Scraped Records: " + str(num))
    try:
        try:
            driver.get(i)
        except:
            print("EXCEPT")
            delete_cache()
            continue

        #Multiple options can be available in one job
        temp_location = []
        temp_work = []
        temp_schedule = []
        temp_school = []
        temp_experience = []

        option_div_el = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="options"]')))
        options = option_div_el.find_elements(By.XPATH, "ul/li")
        for option in options:
            if option.find_element(By.XPATH,'i').get_attribute('innerText') == 'location_on':
                temp_location.append(option.find_element(By.XPATH, 'span').get_attribute('innerText'))
            elif option.find_element(By.XPATH,'i').get_attribute('innerText') == 'work':
                temp_work.append(option.find_element(By.XPATH, 'span').get_attribute('innerText'))
            elif option.find_element(By.XPATH,'i').get_attribute('innerText') == 'schedule':
                temp_schedule.append(option.find_element(By.XPATH, 'span').get_attribute('innerText'))
            elif option.find_element(By.XPATH,'i').get_attribute('innerText') == 'school':
                temp_school.append(option.find_element(By.XPATH, 'span').get_attribute('innerText'))
            elif option.find_element(By.XPATH,'i').get_attribute('innerText') == 'stairs':
                temp_experience.append(option.find_element(By.XPATH, 'span').get_attribute('innerText'))

        if(len(temp_location)==0):
            temp_location.append('None')
        if (len(temp_work) == 0):
            temp_work.append('None')
        if (len(temp_schedule) == 0):
            temp_schedule.append('None')
        if (len(temp_school) == 0):
            temp_school.append('None')
        if (len(temp_experience) == 0):
            temp_experience.append('None')

        #Get the description of the iframe
        try:
            iframe = driver.find_element_by_xpath("//iframe[@id='customJobIframe']")
            driver.switch_to.frame(iframe)
            description.append(driver.find_element(By.XPATH, '/html/body/div[1]').text)
            driver.switch_to.default_content()
        except:
            #Noticed that some of descriptions were in an iframe and some were not.
            try:
                description.append(driver.find_element(By.CSS_SELECTOR, 'div[class="job-view-description-text job-text-max-width"]').text)
            except:
                description.append("")

        try:
            title.append(driver.find_element(By.CSS_SELECTOR,'h2[class="text-copy job-view-title job-text-max-width"]').text)
        except:
            title.append('')
        location.append(str(",".join(temp_location)))
        work.append(str(",".join(temp_work)))
        schedule.append(str(",".join(temp_schedule)))
        school.append(str(",".join(temp_school)))
        experience.append(str(",".join(temp_experience)))
        url.append(driver.current_url)
        new_company_arr.append(company[num])


    except:
        print("SKIP")
        continue
driver.quit()


obj["URL"] = (url)
obj["Company"] = (new_company_arr)
obj["Title"] = (title)
obj["Location"] = (location)
obj["Work"] = (work)
obj["Schedule"] = (schedule)
obj["School"] = (school)
obj["Experience"] = (experience)
obj['Description'] = (description)


df = pd.DataFrame(obj)
df.to_csv('JobsBG-scrape.csv', encoding='utf-8-sig')





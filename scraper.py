import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
import time
import pandas as pd


def get_urls(all_matches_url, headers):
    r = requests.get(all_matches_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    urls = list()
    for a in soup.find_all('a', href=True):
        if '/matches/' in a['href']:
            urls.append(a['href'])

    urls = list(set(urls))
    urls = ['https://www.hltv.org' + x for x in urls]
    return urls

def web_driver_settings():
    # Define the Chrome webdriver options
    options = Options()
    options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability

    # By default, Selenium waits for all resources to download before taking actions.
    # However, we don't need it as the page is populated with dynamically generated JavaScript code.
    options.page_load_strategy = "none"

    # Pass the defined options objects to initialize the web driver 
    driver = Chrome(options=options) 
    # Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
    driver.implicitly_wait(5)
    return driver

def scrape_match_info(match_page_url, match_list, team_name):
    dr = Chrome()
    dr.get(match_page_url)
    print(match_page_url)

    map_holder_elements = dr.find_elements(By.CLASS_NAME, "mapholder")

    for i in range(len(map_holder_elements)):
        match_info = list()
        map = map_holder_elements[i].find_element(By.CLASS_NAME, "mapname").text
        scores = map_holder_elements[i].find_elements(By.CLASS_NAME, "results-team-score")
        teams = map_holder_elements[i].find_elements(By.CLASS_NAME, "results-teamname")

        if( len(scores) < 2 or map == "Default" or (scores[0].text == '-' and scores[1].text == '-') or (teams[0].text != team_name and teams[1].text != team_name)):
            continue


        match_info.append(map)
        match_info.append(scores[0].text)
        match_info.append(scores[1].text)
        match_info.append(teams[0].text)
        match_info.append(teams[1].text)


        if(teams[0].text == team_name and int(scores[0].text) > int(scores[1].text)):
            match_info.append(1)
        elif(teams[1].text == team_name and int(scores[1].text) > int(scores[0].text)):
            match_info.append(1)
        else:
            match_info.append(0)

        match_list.append(match_info)

    dr.close()
    #time.sleep(3)



url = 'https://www.hltv.org/results?team=4494'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://etfdb.com/etfs/asset-class/equity/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


match_list = list()
urls = get_urls(url, headers)
# driver = web_driver_settings()
for match in urls:
    scrape_match_info(match, match_list, "MOUZ")

df = pd.DataFrame(match_list, columns=["Map", "Score1", "Score2", "Team1", "Team2", "MainWon"])
df.to_csv("scraped.csv", index=False)
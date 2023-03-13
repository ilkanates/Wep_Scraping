# selenium
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


# other lib
import time
import os

# bs
from bs4 import BeautifulSoup as bs
import requests

# data
import pandas as pd
import re

# make clickable
from IPython.display import display, HTML
url = "https://jobb.blocket.se/"

job = input("Enter job title : ")
job_title_lst = job.split()
job_search = ""
for i in job_title_lst:
    job_search = job_search + i + "+"
job_search = job_search[:-1]
address = input("Enter address : ")
search_range = input("How many pages do you want to search? : ")
search_range = int(search_range)

# skill_set_string = input("Enter your skills. Use comma to seperate it: ")
# skill_set = skill_set_string.lower().split(",")["for","an"]
skill_set = ["for", "an"]

title_key = "a.header"
corp_key = "a.corp.bold"
date_key = "div.extra>span"
link_key = "a.header"
time_left_key = "table.ui.job-info.very.compact.borderless.fixed.table > tbody > tr> td:nth-child(2)"
location_role_key = "div.column.no-padding>span>a"
job_des_key = "body > div#page-flex-wrapper:nth-child(2) > div#body_content.white-bg:nth-child(4) > div.view:nth-child(4) > div.ui.container:nth-child(3) > div.ui.two.column.stackable.padded.grid > div.seven.wide.column.no-padding-mobile:nth-child(1) > div.ui.container.no-margin-mobile:nth-child(2) > div.ui.padded.grid > div#ad_text_column.ui.column.no-padding > div#job-description:nth-child(1)"

driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")  # create a driver
driver.get(url)  # bring us to the webpage
time.sleep(2.5)  # wait a bit

# click I agree
agree_key = "button.InfoPage__SchibstedButton-sc-3ewdh5-13.InfoPage__AcceptButton-sc-3ewdh5-15.gCzPOF"
agree = driver.find_element(By.CSS_SELECTOR, agree_key)
agree.click()

# find the search bar and enter keywords
search_key1 = "div.ui.left.icon.fluid.large.input.search.category > input.prompt"
search1 = driver.find_element(By.CSS_SELECTOR, search_key1)
search1.send_keys(job)

# find the search bar and enter keywords
search_key2 = "div>input.search"
search2 = driver.find_element(By.CSS_SELECTOR, search_key2)
search2.send_keys(address)

# click the search button
search_key = "div>a.ui.primary.button.fluid"
button_search = driver.find_element(By.CSS_SELECTOR, search_key)
button_search.click()

title_lst = []
corp_lst = []
date_lst = []
link_lst = []
id_lst = []
time_left_lst = []
location_lst = []
role_lst = []
job_des_lst = []
match_lst = []

# Get the page source and create a soup
soup = bs(driver.page_source, "lxml")
containers = soup.select("div.ui.divided.items.unstackable.jobitems > div.item.job-item")

for x in range(0, search_range):
    url = f"https://jobb.blocket.se/lediga-jobb-i-{address}/sida{x}/?ks=freetext.{job_search}"
    html = requests.get(url).content
    soup = bs(html, "lxml")
    containers = soup.select("div.ui.divided.items.unstackable.jobitems>div.item.job-item")

    for i in containers:
        # get title
        title = [j.text.strip() for j in i.select(title_key)]
        corp = [j.text.strip() for j in i.select(corp_key)]
        date = [j.text.strip() for j in i.select(date_key)]
        link = [i['href'] for i in soup.select(link_key)]

        if title:
            title_lst.append(title)
        else:
            title_lst.append(np.nan)

        if corp:
            corp_lst.append(corp)
        else:
            corp_lst.append(np.nan)

        if date:
            date_lst.append(date[0])
        else:
            date_lst.append(np.nan)

    if link:
        for i in link:
            link_lst.append(i)
    else:
        link_lst.append(np.nan)

    if link:
        for i in link:
            match = re.search(r'(\d+#\d+)', i)
            i = match.group(1)
            id_lst.append(i)
    else:
        id_lst.append(np.nan)

    for i in link:
        url = i
        html = requests.get(url).content
        soup = bs(html)
        time_left = [i.text for i in soup.select(time_left_key)][-1]
        location = [i.text for i in soup.select(location_role_key)[1]]
        role = [i.text for i in soup.select(location_role_key)[2]]
        job_des = [i.text for i in soup.select(job_des_key)]

        if time_left:
            time_left_lst.append(time_left)
        else:
            time_left_lst.append(np.nan)

        if location:
            location_lst.append(location)
        else:
            location_lst.append(np.nan)

        if role:
            role_lst.append(role)
        else:
            role_lst.append(np.nan)

        if job_des:
            match = 0
            for skill in skill_set:
                if job_des[0].split().count(skill):
                    match += 1
            match_lst.append(match / len(skill_set) * 100)
        else:
            job_des_lst.append(np.nan)

new_job_lst = job_des[0].split()

x = 0
for i in skill_set:
    if new_job_lst.count(i):
        x += 1
len(skill_set)

# df
df = pd.DataFrame({
    "Id": id_lst,
    "Title": title_lst,
    "Corperation": corp_lst,
    "Created Date": date_lst,
    "Last Apply Date": time_left_lst,
    "Location": location_lst,
    "Role Area": role_lst,
    "Link": link_lst,
    "Match": match_lst
})
df = df.drop_duplicates(subset='Id', keep='first')
df['Link'] = '<a href="' + df['Link'].astype(str) + '">Link</a>'
display(HTML(df.to_html(escape=False)))

print("Done!!!")
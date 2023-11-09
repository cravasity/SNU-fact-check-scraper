from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

website = "https://factcheck.snu.ac.kr/"
driver = webdriver.Chrome()
driver.get(website)


def init():
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div[3]/button[2]').click()
    time.sleep(0.5)

def crawl():
    sourceurl = []
    data = [] 

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "div")))

    titles = driver.div_elements = driver.find_elements(By.CSS_SELECTOR, "div[class^='jsx-'][class$='fact-check-title']")
    sources = driver.div_elements = driver.find_elements(By.CSS_SELECTOR, "div[class^='jsx-'][class$='fact-check-source']")
    labels = driver.div_elements = driver.find_elements(By.CSS_SELECTOR, "div[class^='jsx-'][class$='fact-dial-label-text']")

    for elem in sources:
        try:
            element = elem.find_element(By.TAG_NAME, "a")
            if element:
                val = element.get_attribute("href")
        except NoSuchElementException as e:
            val = 'url not available'

        sourceurl.append(val)

    for elem1, elem2, elem3, elem4 in zip(titles, sources, labels, sourceurl):
        data.append([elem1.text, elem2.text, elem3.text, elem4])

    return data

def nextpage(i):
    page_number = str(i)
    button = driver.find_element(By.XPATH, f"//button[contains(@class, 'page-index-button btn btn-outline-secondary btn-sm') and text()='{page_number}']")
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    time.sleep(1)
    button.click()

def main():
    x = 5 #pages to crawl
    scraped_data = []

    for i in range(2):
        init()

    for i in range(2,x+2):
        scraped_data.extend(crawl())
        nextpage(i)
        time.sleep(0.7)
    
    save_path = 'c:/Users/AAA/Desktop/output/' #path to save output csv
    df = pd.DataFrame(scraped_data, columns=['제목', '출처', 'label', '링크'])
    df.to_csv(save_path + 'scraped_data.csv', index=False)


main()
time.sleep(3)
driver.quit()


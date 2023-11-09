from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import pandas as pd
import sys
import time

website_categories = {
    "정치": "https://factcheck.snu.ac.kr/?topic_id=1",
    "경제": "https://factcheck.snu.ac.kr/?topic_id=2",
    "국제": "https://factcheck.snu.ac.kr/?topic_id=3",
    "사회": "https://factcheck.snu.ac.kr/?topic_id=4",
    "문화": "https://factcheck.snu.ac.kr/?topic_id=5",
    "IT/과학": "https://factcheck.snu.ac.kr/?topic_id=6",
    "기타": "https://factcheck.snu.ac.kr/?topic_id=7",
    "교차검증": "https://factcheck.snu.ac.kr/?orderType=hot",
    "코로나19": "https://factcheck.snu.ac.kr/?tag_id=4",
    "코로나 백신": "https://factcheck.snu.ac.kr/?tag_id=8",
    "후쿠시마": "https://factcheck.snu.ac.kr/?tag_id=15",
}

labels = ["판단유보", "전혀 사실 아님", "대체로 사실 아님", "절반의 사실", "대체로 사실", "사실", "전체 라벨"]

def get_website_url_and_category():
    while True:
        try:
            user_choice = int(input("\n정보 수집 기준을 선택하십시오:\n"
                                    "1. 주제별 기사 수집\n"
                                    "2. 사실여부 기준 기사 수집\n"
                                    "3. 기준 없음 (사이트 전체 수집)\n"
                                    "원하는 번호를 입력하세요: "))

            if user_choice == 1:
                print("Available website categories:")
                for idx, category_key in enumerate(website_categories.keys(), start=1):
                    print(f"{idx}. {category_key}")

                category_choice = int(input("Enter the number corresponding to the website category: "))
                if 1 <= category_choice <= len(website_categories):
                    selected_category = list(website_categories.values())[category_choice - 1]
                    selected_key = list(website_categories.keys())[category_choice - 1]
                    return selected_category, selected_key
                else:
                    print("Invalid input. Please enter a valid number.")

            elif user_choice == 2:
                score = int(input("\n판정 결과 (라벨)을 기준으로 정보를 수집하겠습니까?\n"+
                              "6 = 라벨 전체 보기\n" +
                              "5 = '사실'만 보기\n" +
                              "4 = '대체로 사실'만 보기\n" +
                              "3 = '절반의 사실'만 보기\n" +
                              "2 = '대체로 사실 아님'만 보기\n" +
                              "1 = '전혀 사실 아님'만 보기\n" +
                              "0 = '판단유보'만 보기\n"
                              ))
                if 0 <= score <= 6:
                    if score == 6:
                        return "https://factcheck.snu.ac.kr/", labels[score]
                    else:
                        return f"https://factcheck.snu.ac.kr/?score={score}", labels[score]
                else:
                    print("Invalid input. Please enter a score between 0 and 6.")
            
            elif user_choice == 3:
                return "https://factcheck.snu.ac.kr/", labels[6]

            else:
                print("Invalid choice. Please enter either 1, 2 or 3.\n")

        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")

def get_num_pages():
    while True:
        try:
            num_pages = int(input("크롤링 할 페이지 수를 입력하시오: "))
            if num_pages > 0:
                return num_pages
            else:
                print("Invalid input. Please enter a positive integer.")

        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def init(driver):
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div[3]/button[2]').click()
    time.sleep(0.5)

def crawl(driver):
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

def nextpage(driver, i, scraped_data, file_name):
    try:
        page_number = str(i)
        button = driver.find_element(By.XPATH, f"//button[contains(@class, 'page-index-button btn btn-outline-secondary btn-sm') and text()='{page_number}']")
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)
        button.click()
    except NoSuchElementException:
        num_scraped_pages = i - 1
        print(f"No more pages available. Scraped {num_scraped_pages} pages. Terminating the scraping process.")
        save_csv(scraped_data, file_name)
        time.sleep(1)
        driver.quit()
        sys.exit()

def save_csv(scraped_data, file_name):
    save_path = 'c:/Users/AAA/Desktop/output/'  # path to save output csv
    df = pd.DataFrame(scraped_data, columns=['제목', '출처', 'label', '링크'])
    df.to_csv(save_path + file_name, index=False)
    print(f"CSV file saved at: {save_path}{file_name}")

def main():
    website, category = get_website_url_and_category()
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M")
    file_name = f"{current_datetime}_{category}.csv"
    driver = webdriver.Chrome()
    driver.get(website)

    num_pages = get_num_pages()
    scraped_data = []

    for i in range(2):
        init(driver)

    for i in range(2,num_pages+2):
        scraped_data.extend(crawl(driver))
        nextpage(driver, i, scraped_data, file_name)
        time.sleep(1)
    
    save_csv(scraped_data, file_name)
    time.sleep(1)
    driver.quit()

if __name__ == "__main__":
    main()



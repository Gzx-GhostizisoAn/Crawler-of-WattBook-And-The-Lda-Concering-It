import pandas as pd
import os
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

CHROME_DRIVER_PATH = './chromedriver.exe'
INPUT_EXCEL = 'books.xlsx'
OUTPUT_CSV = 'scraped_descriptions.csv'
DONE_LIST_CSV = "done_list.csv"
TIMEOUT = 10


# 初始化 CSV 
def init_csv_files():
    if not os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Bookid", "Title", "merged"])

    if not os.path.exists(DONE_LIST_CSV):
        with open(DONE_LIST_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Bookid", "Title", "Success", "Status"])


def save_one_result(bookid, title, merged_text):
    with open(OUTPUT_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([bookid, title, merged_text])


def save_done_status(bookid, title, success, status):
    with open(DONE_LIST_CSV, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([bookid, title, success, status])


def init_driver():
    service = Service(CHROME_DRIVER_PATH)
    options = Options()
    options.add_argument("--headless=new")
    return webdriver.Chrome(service=service, options=options)


def scrape_description(driver, story_url):
    try:
        driver.get(story_url)
        wait = WebDriverWait(driver, TIMEOUT)
        desc_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//pre[contains(@class,"mpshL")]'))
        )
        return desc_element.text.strip()
    except TimeoutException:
        return None


def main():
    init_csv_files()

    try:
        df = pd.read_excel(INPUT_EXCEL)
        print(f"成功读取 {len(df)} 条书籍记录")
    except Exception as e:
        print(f"读取 Excel 失败: {e}")
        return

    driver = init_driver()

    try:
        total = len(df)
        for idx, row in df.iterrows():
            bookid = row["Bookid"]
            title = row["Title"]
            link = row["Link"]

            print(f"\n[{idx+1}/{total}] 正在爬取: {title}")

            desc = scrape_description(driver, link)

            if desc and len(desc.strip()) > 10:
                save_one_result(bookid, title, desc)
                save_done_status(bookid, title, 1, "Success")
                print(f" → 成功抓取 ({len(desc)} 字符)")
            else:
                save_one_result(bookid, title, "抓取失败/无摘要")
                save_done_status(bookid, title, 0, "Fail or Empty")
                print(" → 失败")

            time.sleep(random.uniform(1.5, 3.0))

    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    main()

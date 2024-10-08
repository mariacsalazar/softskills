import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import logging
import time
import json
import random
import socket
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

class ChromiumPage:
    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--lang=en-US,en;q=0.9')
        options.add_argument('--remote-debugging-port=9222')  # 添加这行
        
        user_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'chrome_user_data'))
        options.add_argument(f'user-data-dir="{user_data_dir}"')
        
        options.add_argument('--dns-servers=8.8.8.8,8.8.4.4')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        try:
            self.driver = uc.Chrome(options=options)
            stealth(self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
            )
        except Exception as e:
            logging.error(f"创建 Chrome 实例时发生错误: {e}")
            raise

    def get(self, url):
        self.driver.get(url)

    def find_element(self, by, value):
        return self.driver.find_element(by, value)

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def quit(self):
        self.driver.quit()

    def get_page_source(self):
        return self.driver.page_source

    def get_current_url(self):
        return self.driver.current_url

def wait_for_page_load(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        return True
    except TimeoutException:
        return False

def find_and_input(driver, selectors, text, timeout=30):
    for selector in selectors:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            logging.info(f"已在 {selector} 输入: {text}")
            return True
        except Exception as e:
            logging.warning(f"无法在 {selector} 输入文本: {e}")
    logging.error("所有选择器都失败了")
    return False

def click_search_button(driver, timeout=30):
    search_button_selectors = [
        "button.jobs-search-box__submit-button",
        "button[aria-label='Search']",
        "button[type='submit']"
    ]
    for selector in search_button_selectors:
        try:
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            button.click()
            logging.info(f"已点击搜索按钮: {selector}")
            return True
        except Exception as e:
            logging.warning(f"无法点击搜索按钮 {selector}: {e}")
    logging.error("无法找到或点击任何搜索按钮")
    return False

def save_search_results(driver):
    jobs = []
    max_jobs = 100  # 设置最大工作卡片数量为100
    page_num = 1
    same_count = 0
    max_same_count = 3  # 将这个值从5改为3
    try:
        while len(jobs) < max_jobs:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
            )
            
            # 找到工作卡片容器
            job_list_container = driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
            
            # 渐进滚动加载更多工作卡片
            last_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
            scroll_attempt = 0
            last_job_count = 0
            while True:
                # 计算滚动距离（调整为容器高度的10%）
                scroll_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
                scroll_top = driver.execute_script("return arguments[0].scrollTop", job_list_container)
                scroll_distance = min(scroll_height * 0.1, scroll_height - scroll_top)
                
                # 滚动
                driver.execute_script("arguments[0].scrollTop += arguments[1];", job_list_container, scroll_distance)
                
                # 等待页面加载
                time.sleep(3)
                
                # 检查是否到达底部或没有更多工作
                new_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
                current_job_cards = job_list_container.find_elements(By.CSS_SELECTOR, ".job-card-container")
                logging.info(f"当前已加载 {len(current_job_cards)} 个工作卡片")
                
                if len(current_job_cards) == last_job_count:
                    same_count += 1
                else:
                    same_count = 0
                
                if same_count >= max_same_count:
                    logging.info("连续3次加载相同数量的工作卡片，尝试点击'查看更多工作'按钮")
                    try:
                        see_more_jobs_button = driver.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button")
                        see_more_jobs_button.click()
                        time.sleep(5)  # 等待新的工作加载
                        same_count = 0
                    except Exception as e:
                        logging.warning(f"无法找到或点击'查看更多工作'按钮: {e}")
                        break
                
                if new_height == last_height and len(current_job_cards) == last_job_count:
                    scroll_attempt += 1
                    if scroll_attempt >= 5:
                        logging.info("似乎已到达底部或无法加载更多工作")
                        break
                else:
                    scroll_attempt = 0
                    last_height = new_height
                    last_job_count = len(current_job_cards)
                
                # 如果新增了工作卡片，重置计数器并等待更长时间
                if len(current_job_cards) > last_job_count:
                    logging.info(f"加载了新的工作卡片，从 {last_job_count} 增加到 {len(current_job_cards)}")
                    scroll_attempt = 0
                    time.sleep(2)  # 额外等待时间
            
            # 提取当前页面的工作卡片
            job_cards = job_list_container.find_elements(By.CSS_SELECTOR, ".job-card-container")
            logging.info(f"开始提取 {len(job_cards)} 个工作卡片的信息")
            for index, card in enumerate(job_cards):
                if len(jobs) >= max_jobs:
                    break
                try:
                    job_info = extract_job_info(card)
                    jobs.append(job_info)
                    logging.info(f"Job {len(jobs)}/{max_jobs} link: {job_info.get('link', 'No link found')}")
                except Exception as e:
                    logging.error(f"处理第 {index + 1} 个职位时发生错误: {e}")
            
            if len(jobs) >= max_jobs:
                break
            
            # 如果没有找到更多工作，退出循环
            if len(jobs) == last_job_count:
                logging.info("没有找到更多工作，结束搜索")
                break
            
            last_job_count = len(jobs)
        
        total_jobs = len(jobs)
        logging.info(f"总共找到 {total_jobs} 个工作卡片")
        
        with open("job_listings.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
        logging.info(f"已保存 {total_jobs} 个职位列表到 job_listings.json")
        
        return jobs
    except Exception as e:
        logging.error(f"提取职位信息时发生错误: {e}")
        with open("error_job_listings_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.info("已保存错误页面到 error_job_listings_page.html")
        return jobs  # 返回已经收集到的工作，即使发生错误

def extract_job_info(card):
    job_info = {}
    selectors = {
        "title": ".job-card-list__title",
        "company": ".job-card-container__primary-description",
        "location": ".job-card-container__metadata-item",
        "job_insight": ".job-card-container__job-insight-text",  # 可能需要更新这个选择器
    }

    for key, selector in selectors.items():
        try:
            element = WebDriverWait(card, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            job_info[key] = element.text
        except Exception as e:
            logging.warning(f"无法找到 {key}: {e}")
            job_info[key] = f"未找到{key}"  # 或者可以设置为 None

    # 使用 JavaScript 提取链接
    try:
        link = card.parent.execute_script("""
            var element = arguments[0];
            var link = element.querySelector('a[href*="/jobs/view/"]');
            return link ? link.href : null;
        """, card)
        job_info['link'] = link if link else "未找到link"
    except Exception as e:
        logging.warning(f"无法找到链接: {e}")
        job_info['link'] = "未找到link"

    try:
        footer_items = card.find_elements(By.CSS_SELECTOR, ".job-card-container__footer-item")
        job_info["footer_info"] = [item.text for item in footer_items]
    except Exception as e:
        logging.warning(f"无法找到页脚信息: {e}")
        job_info["footer_info"] = []

    return job_info

def check_linkedin_accessibility():
    try:
        response = requests.get("https://www.linkedin.com", timeout=10)
        if response.status_code == 200:
            logging.info("LinkedIn 网站可以访问")
            return True
        else:
            logging.warning(f"LinkedIn 返回了非 200 状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        logging.error(f"无法访问 LinkedIn: {str(e)}")
        return False

def open_linkedin_jobs_search():
    try:
        page = ChromiumPage()
    except Exception as e:
        logging.error(f"无法创建 ChromiumPage 实例: {e}")
        return

    try:
        logging.info("正在打开 LinkedIn Jobs 搜索页面...")
        page.get("https://www.linkedin.com/jobs/search/")

        if not wait_for_page_load(page.driver):
            logging.error("页面加载超时")
            return

        logging.info("LinkedIn Jobs 搜索页面已成功打开。")
        logging.info("当前 URL: %s", page.get_current_url())

        job_input = input("请输入要搜索的职位: ")
        location_input = input("请输入要搜索的地理位置: ")

        job_selectors = [
            "input[aria-label='役職やスキル、会社名で検索']",
            "input[aria-label='Search job titles or companies']",
            "input.jobs-search-box__text-input[name='keywords']"
        ]
        location_selectors = [
            "input[aria-label='都道府県、市区町村、または郵便番号']",
            "input[aria-label='City, state, or zip code']",
            "input.jobs-search-box__text-input[name='location']"
        ]

        if find_and_input(page.driver, job_selectors, job_input) and \
           find_and_input(page.driver, location_selectors, location_input):
            if click_search_button(page.driver):
                logging.info("已执行搜索")
                random_delay(5, 10)
                jobs = save_search_results(page.driver)
                
                if jobs:
                    process_job_links(page.driver, jobs)
                else:
                    logging.error("没有找到任何职位信息")
            else:
                logging.error("无法执行搜索")
        else:
            logging.error("无法输入搜索条件")

        logging.info("搜索结果已自动保存。")
        input("操作已完成。请手动查看浏览器，完成后按回车键关闭浏览器...")

    except WebDriverException as e:
        logging.error(f"WebDriver 异常: {e}")
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
    finally:
        try:
            page.quit()
        except:
            pass
        logging.info("脚本执行完毕。")

def cleanup():
    try:
        os.system("taskkill /f /im chrome.exe")
        os.system("taskkill /f /im chromedriver.exe")
    except:
        pass

def get_job_details(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-view-layout"))
        )
        
        # 「さらに表示」ボタンをクリック
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-description__footer-button"))
            )
            show_more_button.click()
            logging.info("「さらに表示」ボタンをクリックしました")
        except Exception as e:
            logging.warning(f"「さらに表示」ボタンをクリックできませんでした: {e}")
        
        # 少し待機して、追加情報が表示されるのを待つ
        time.sleep(2)
        
        job_details = {}
        
        # 提取職位標題
        try:
            job_details['title'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title, .topcard__title"))
            ).text
        except:
            job_details['title'] = "未找到标题"
        
        # 提取公司名称
        try:
            job_details['company'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name, .topcard__org-name-link"))
            ).text
        except:
            job_details['company'] = "未找到公司名称"
        
        # 提取位置
        try:
            job_details['location'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__bullet, .topcard__flavor--bullet"))
            ).text
        except:
            job_details['location'] = "未找到位置信息"
        
        # 提取職位描述
        try:
            job_details['description'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-description__content, .description__text"))
            ).text
        except:
            job_details['description'] = "未找到职位描述"
        
        # 提取其他可能的詳細信息
        try:
            criteria_elements = driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-item")
            for element in criteria_elements:
                try:
                    key = element.find_element(By.CSS_SELECTOR, ".description__job-criteria-subheader").text
                    value = element.find_element(By.CSS_SELECTOR, ".description__job-criteria-text").text
                    job_details[key] = value
                except:
                    pass
        except:
            logging.warning("无法提取额外的工作信息")

        return job_details
    except Exception as e:
        logging.error(f"获取职位详情时发生错误: {e}")
        return None

def save_job_details(job_details, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(job_details, f, ensure_ascii=False, indent=4)

def process_job_links(driver, jobs):
    for index, job in enumerate(jobs):
        link = job.get('link')
        if link and link != "未找到link":
            logging.info(f"正在处理第 {index + 1} 个职位链接: {link}")
            try:
                job_details = get_job_details(driver, link)
                if job_details:
                    filename = f"job_details_{index + 1}.json"
                    save_job_details(job_details, filename)
                    logging.info(f"已保存职位详情到 {filename}")
                else:
                    logging.warning(f"无法获取第 {index + 1} 个职位的详细信息")
            except Exception as e:
                logging.error(f"处理第 {index + 1} 个职位时发生错误: {e}")
        else:
            logging.warning(f"第 {index + 1} 个职位没有有效的链接")
        
        random_delay(2, 5)  # 在处理每个职位之间添加随机延迟

# 在主函数开始时调用
if __name__ == "__main__":
    cleanup()
    if check_linkedin_accessibility():
        open_linkedin_jobs_search()
    else:
        print("无法访问 LinkedIn 网站。请检查您的网络连接或者 LinkedIn 是否在您的地区可用。")
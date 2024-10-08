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
        options.add_argument('--remote-debugging-port=9222')  # Add this line
        
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
            logging.error(f"Error creating Chrome instance: {e}")
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
            logging.info(f"Input text '{text}' in {selector}")
            return True
        except Exception as e:
            logging.warning(f"Unable to input text in {selector}: {e}")
    logging.error("All selectors failed")
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
            logging.info(f"Clicked search button: {selector}")
            return True
        except Exception as e:
            logging.warning(f"Unable to click search button {selector}: {e}")
    logging.error("Unable to find or click any search buttons")
    return False

def save_search_results(driver):
    jobs = []
    max_jobs = 100  # Set the max job cards to 100
    page_num = 1
    same_count = 0
    max_same_count = 3  # Adjust this value from 5 to 3
    try:
        while len(jobs) < max_jobs:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-container"))
            )
            
            # Find job card container
            job_list_container = driver.find_element(By.CSS_SELECTOR, ".jobs-search-results-list")
            
            # Gradually scroll to load more job cards
            last_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
            scroll_attempt = 0
            last_job_count = 0
            while True:
                # Calculate scroll distance (adjust to 10% of container height)
                scroll_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
                scroll_top = driver.execute_script("return arguments[0].scrollTop", job_list_container)
                scroll_distance = min(scroll_height * 0.1, scroll_height - scroll_top)
                
                # Scroll
                driver.execute_script("arguments[0].scrollTop += arguments[1];", job_list_container, scroll_distance)
                
                # Wait for the page to load
                time.sleep(3)
                
                # Check if reached the bottom or no more jobs to load
                new_height = driver.execute_script("return arguments[0].scrollHeight", job_list_container)
                current_job_cards = job_list_container.find_elements(By.CSS_SELECTOR, ".job-card-container")
                logging.info(f"Currently loaded {len(current_job_cards)} job cards")
                
                if len(current_job_cards) == last_job_count:
                    same_count += 1
                else:
                    same_count = 0
                
                if same_count >= max_same_count:
                    logging.info("Loaded the same number of job cards 3 times in a row, trying to click 'See more jobs'")
                    try:
                        see_more_jobs_button = driver.find_element(By.CSS_SELECTOR, "button.infinite-scroller__show-more-button")
                        see_more_jobs_button.click()
                        time.sleep(5)  # Wait for new jobs to load
                        same_count = 0
                    except Exception as e:
                        logging.warning(f"Unable to find or click 'See more jobs' button: {e}")
                        break
                
                if new_height == last_height and len(current_job_cards) == last_job_count:
                    scroll_attempt += 1
                    if scroll_attempt >= 5:
                        logging.info("Reached bottom or unable to load more jobs")
                        break
                else:
                    scroll_attempt = 0
                    last_height = new_height
                    last_job_count = len(current_job_cards)
                
                # If new job cards are loaded, reset counter and wait longer
                if len(current_job_cards) > last_job_count:
                    logging.info(f"New job cards loaded, from {last_job_count} to {len(current_job_cards)}")
                    scroll_attempt = 0
                    time.sleep(2)  # Additional wait time
            
            # Extract job cards from the current page
            job_cards = job_list_container.find_elements(By.CSS_SELECTOR, ".job-card-container")
            logging.info(f"Starting to extract {len(job_cards)} job card info")
            for index, card in enumerate(job_cards):
                if len(jobs) >= max_jobs:
                    break
                try:
                    job_info = extract_job_info(card)
                    jobs.append(job_info)
                    logging.info(f"Job {len(jobs)}/{max_jobs} link: {job_info.get('link', 'No link found')}")
                except Exception as e:
                    logging.error(f"Error processing job {index + 1}: {e}")
            
            if len(jobs) >= max_jobs:
                break
            
            # If no more jobs are found, exit the loop
            if len(jobs) == last_job_count:
                logging.info("No more jobs found, ending search")
                break
            
            last_job_count = len(jobs)
        
        total_jobs = len(jobs)
        logging.info(f"Total {total_jobs} job cards found")
        
        with open("job_listings.json", "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved {total_jobs} job listings to job_listings.json")
        
        return jobs
    except Exception as e:
        logging.error(f"Error extracting job info: {e}")
        with open("error_job_listings_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logging.info("Saved error page to error_job_listings_page.html")
        return jobs  # Return jobs even if an error occurs

def extract_job_info(card):
    job_info = {}
    selectors = {
        "title": ".job-card-list__title",
        "company": ".job-card-container__primary-description",
        "location": ".job-card-container__metadata-item",
        "job_insight": ".job-card-container__job-insight-text",  # This selector might need an update
    }

    for key, selector in selectors.items():
        try:
            element = WebDriverWait(card, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            job_info[key] = element.text
        except Exception as e:
            logging.warning(f"Unable to find {key}: {e}")
            job_info


   # Use JavaScript to extract the link
try:
    link = card.parent.execute_script("""
        var element = arguments[0];
        var link = element.querySelector('a[href*="/jobs/view/"]');
        return link ? link.href : null;
    """, card)
    job_info['link'] = link if link else "Link not found"
except Exception as e:
    logging.warning(f"Unable to find the link: {e}")
    job_info['link'] = "Link not found"

try:
    footer_items = card.find_elements(By.CSS_SELECTOR, ".job-card-container__footer-item")
    job_info["footer_info"] = [item.text for item in footer_items]
except Exception as e:
    logging.warning(f"Unable to find footer information: {e}")
    job_info["footer_info"] = []

return job_info

def check_linkedin_accessibility():
    try:
        response = requests.get("https://www.linkedin.com", timeout=10)
        if response.status_code == 200:
            logging.info("LinkedIn website is accessible")
            return True
        else:
            logging.warning(f"LinkedIn returned a non-200 status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        logging.error(f"Unable to access LinkedIn: {str(e)}")
        return False

def open_linkedin_jobs_search():
    try:
        page = ChromiumPage()
    except Exception as e:
        logging.error(f"Unable to create ChromiumPage instance: {e}")
        return

    try:
        logging.info("Opening LinkedIn Jobs search page...")
        page.get("https://www.linkedin.com/jobs/search/")

        if not wait_for_page_load(page.driver):
            logging.error("Page load timeout")
            return

        logging.info("LinkedIn Jobs search page opened successfully.")
        logging.info("Current URL: %s", page.get_current_url())

        job_input = input("Please enter the job title to search: ")
        location_input = input("Please enter the location to search: ")

        job_selectors = [
            "input[aria-label='Search by title, skill, or company']",
            "input[aria-label='Search job titles or companies']",
            "input.jobs-search-box__text-input[name='keywords']"
        ]
        location_selectors = [
            "input[aria-label='City, state, or zip code']",
            "input.jobs-search-box__text-input[name='location']"
        ]

        if find_and_input(page.driver, job_selectors, job_input) and \
           find_and_input(page.driver, location_selectors, location_input):
            if click_search_button(page.driver):
                logging.info("Search executed")
                random_delay(5, 10)
                jobs = save_search_results(page.driver)
                
                if jobs:
                    process_job_links(page.driver, jobs)
                else:
                    logging.error("No job information found")
            else:
                logging.error("Unable to execute search")
        else:
            logging.error("Unable to input search criteria")

        logging.info("Search results have been automatically saved.")
        input("Operation completed. Please manually check the browser, press Enter when done to close the browser...")

    except WebDriverException as e:
        logging.error(f"WebDriver exception: {e}")
    except Exception as e:
        logging.error(f"An unknown error occurred: {e}")
    finally:
        try:
            page.quit()
        except:
            pass
        logging.info("Script execution complete.")

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
        
        # Click the "Show More" button
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.jobs-description__footer-button"))
            )
            show_more_button.click()
            logging.info("Clicked the 'Show More' button")
        except Exception as e:
            logging.warning(f"Unable to click 'Show More' button: {e}")
        
        # Wait for additional information to load
        time.sleep(2)
        
        job_details = {}
        
        # Extract job title
        try:
            job_details['title'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__job-title, .topcard__title"))
            ).text
        except:
            job_details['title'] = "Title not found"
        
        # Extract company name
        try:
            job_details['company'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name, .topcard__org-name-link"))
            ).text
        except:
            job_details['company'] = "Company name not found"
        
        # Extract location
        try:
            job_details['location'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__bullet, .topcard__flavor--bullet"))
            ).text
        except:
            job_details['location'] = "Location information not found"
        
        # Extract job description
        try:
            job_details['description'] = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-description__content, .description__text"))
            ).text
        except:
            job_details['description'] = "Job description not found"
        
        # Extract other potential details
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
            logging.warning("Unable to extract additional job information")

        return job_details
    except Exception as e:
        logging.error(f"Error fetching job details: {e}")
        return None

def save_job_details(job_details, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(job_details, f, ensure_ascii=False, indent=4)

def process_job_links(driver, jobs):
    for index, job in enumerate(jobs):
        link = job.get('link')
        if link and link != "Link not found":
            logging.info(f"Processing job link {index + 1}: {link}")
            try:
                job_details = get_job_details(driver, link)
                if job_details:
                    filename = f"job_details_{index + 1}.json"
                    save_job_details(job_details, filename)
                    logging.info(f"Saved job details to {filename}")
                else:
                    logging.warning(f"Unable to fetch details for job {index + 1}")
            except Exception as e:
                logging.error(f"Error processing job {index + 1}: {e}")
        else:
            logging.warning(f"Job {index + 1} has no valid link")
        
        random_delay(2, 5)  # Add a random delay between processing each job

# Call this at the start of the main function
if __name__ == "__main__":
    cleanup()
    if check_linkedin_accessibility():
        open_linkedin_jobs_search()
    else:
        print("Unable to access LinkedIn website. Please check your network connection or if LinkedIn is available in your region.")

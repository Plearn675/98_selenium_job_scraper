import time
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # Added for dropdowns
from webdriver_manager.chrome import ChromeDriverManager




class JobScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def perform_search(self, keyword, location_name):
        self.driver.maximize_window()
        self.driver.get("https://www.net-empregos.com/")

        # a. HANDLE COOKIES
        try:
            cookie_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
            cookie_button.click()
            print("Cookies accepted!")
            time.sleep(5)
        except Exception:
            print("Cookie banner not found.")

        # b. HANDLE ALERTS
        try:
            no_alert_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Não Ativar')]")))
            no_alert_button.click()
            print("Alerts declined!")
            time.sleep(2)
        except Exception:
            print("Alert pop-up did not appear.")

        # c. SELECT CATEGORY
        try:
            # We wait for the dropdown and select the category
            category_el = self.wait.until(EC.presence_of_element_located((By.ID, "categoria")))
            category_dropdown = Select(category_el)
            category_dropdown.select_by_visible_text("Informática ( Programação )")
            print("Category 'Informática ( Programação )' selected!")
            # Small sleep to let the site update after the selection
            time.sleep(1)
        except Exception:
            print("Could not select category.")

        # d. CLICK PESQUISAR (The "Super Click" version)
        try:
            search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "pesquisar")))

            # Method 1: Scroll to it first (prevents "Element Click Intercepted")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)

            # Method 2: Use the ENTER key (often works when mouse clicks fail)
            from selenium.webdriver.common.keys import Keys
            search_button.send_keys(Keys.ENTER)
            print("Search triggered via ENTER key!")

        except Exception:
            try:
                # Method 3: The JavaScript Force Click
                self.driver.execute_script("arguments[0].click();", search_button)
                print("Search triggered via JS Force Click!")
            except:
                print("Could not trigger search.")

        # IMPORTANT: Wait for the URL to change or a result element to appear
        # This prevents the script from trying to scrape the old page
        time.sleep(5)

    def get_results(self):
        print("Scraping results...")
        try:
            # 1. Wait for at least one job link to be present
            # This is better than a fixed sleep because it moves as soon as the data is ready
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oferta-link")))

            # 2. Use the exact class you found in the inspector
            job_elements = self.driver.find_elements(By.CLASS_NAME, "oferta-link")

            jobs_found = []
            for el in job_elements:
                title = el.text.strip()
                link = el.get_attribute("href")

                # Check that we have a valid title and link
                if title and link:
                    # Prevent adding the same job twice
                    if link not in [j['link'] for j in jobs_found]:
                        jobs_found.append({
                            "title": title,
                            "link": link
                        })

            print(f"Extraction successful! Found {len(jobs_found)} jobs.")
            return jobs_found

        except Exception as e:
            print(f"Scraping failed or timed out: {e}")
            # As a final backup, let's try a broader search if the class search fails
            return self.get_results_backup()

    def get_results_backup(self):
        # Broad fallback if 'oferta-link' isn't found for some reason
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'oferta-de-emprego')]")
        return [{"title": l.text.strip(), "link": l.get_attribute("href")} for l in links if l.text.strip()]
    def quit(self):
        """Safely closes the browser window"""
        if self.driver:
            self.driver.quit()
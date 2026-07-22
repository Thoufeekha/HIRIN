from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


class TechnoparkScraper:
    source_name = "technopark"
    url = "https://technopark.in/job-search"
    base_url = "https://technopark.in"

    def fetch(self, driver, page_url, wait_selector):
        driver.get(page_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        return driver.page_source

    def parse_list(self, html):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        cards = soup.select('a[class*="shadow-2xl"]')

        for card in cards:
            job_url = card.get("href", "").strip()
            if job_url and not job_url.startswith("http"):
                job_url = self.base_url + job_url

            title_tag = card.select_one("h4.bodyemphasis")
            title = title_tag.get_text(strip=True) if title_tag else ""

            text = card.get_text(separator="\u241E", strip=True)
            parts = [p.strip() for p in text.split("\u241E") if p.strip()]

            closing_date = ""
            company = ""

            for part in parts:
                if "Closing Date" in part:
                    closing_date = part.replace("Closing Date:", "").strip()
                elif "Posted On" in part:
                    pass
                elif part != title:
                    if not company:
                        company = part

            valid_until = None
            if closing_date:
                try:
                    valid_until = datetime.strptime(closing_date, "%d.%b %Y").date()
                except ValueError:
                    valid_until = None

            if not valid_until:
                valid_until = (datetime.now() + timedelta(days=30)).date()

            if title and job_url:
                jobs.append({
                    "title": title,
                    "company": company or "Unknown",
                    "location": "Trivandrum",
                    "url": job_url,
                    "valid_until": valid_until,
                    "description": "",
                    "skills": "",
                })

        return jobs

    def parse_detail(self, html):
        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.select_one('div[class*="_mce-content-body"]')

        if not content_div:
            return "", ""

        paragraphs = [p.get_text(strip=True) for p in content_div.find_all("p")]
        paragraphs = [p for p in paragraphs if p]

        full_text = "\n".join(paragraphs)

        skill_headers = ["Preferred Skills", "Required Skills", "Skills Required", "Key Skills"]
        stop_headers = ["Educational Qualification", "Salary Package", "Education", "Qualification"]

        capturing = False
        skill_lines = []

        for p in paragraphs:
            if any(h in p for h in skill_headers):
                capturing = True
                continue
            if any(h in p for h in stop_headers):
                capturing = False
            if capturing:
                skill_lines.append(p)

        skills_text = ", ".join(skill_lines)

        return full_text, skills_text

    def run(self):
        driver = get_driver()
        jobs = []

        try:
            list_html = self.fetch(driver, self.url, 'a[class*="shadow-2xl"]')
            jobs = self.parse_list(list_html)

            for job in jobs:
                try:
                    detail_html = self.fetch(driver, job["url"], 'div[class*="_mce-content-body"]')
                    description, skills = self.parse_detail(detail_html)
                    job["description"] = description
                    job["skills"] = skills
                except Exception:
                    job["description"] = ""
                    job["skills"] = ""
        finally:
            driver.quit()

        return jobs

class InfoparkScraper:
    source_name = "infopark"
    url = "https://infopark.in/companies-job"
    base_url = "https://infopark.in"

    def fetch(self, driver, page_url, wait_selector):
        driver.get(page_url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        return driver.page_source

    def parse_list(self, html):
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        rows = soup.select('div#job-list table tbody tr')

        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue

            posted_date = cells[0].get_text(strip=True)
            title = cells[1].get_text(strip=True)
            company = cells[2].get_text(strip=True)
            last_date = cells[3].get_text(strip=True)

            link_tag = cells[4].select_one("a")
            job_url = link_tag.get("href", "").strip() if link_tag else ""
            if job_url and not job_url.startswith("http"):
                job_url = self.base_url + job_url

            valid_until = None
            if last_date:
                try:
                    valid_until = datetime.strptime(last_date, "%d %b %Y").date()
                except ValueError:
                    valid_until = None

            if not valid_until:
                valid_until = (datetime.now() + timedelta(days=30)).date()

            if title and job_url:
                jobs.append({
                    "title": title,
                    "company": company or "Unknown",
                    "location": "Infopark",
                    "url": job_url,
                    "valid_until": valid_until,
                    "description": "",
                    "skills": "",
                })

        return jobs

    def parse_detail(self, html):
        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.select_one('div.company-detail.career-op')

        if not content_div:
            return "", ""
        
        tags = content_div.find_all(["p", "li", "h2", "h3", "h4"])
        paragraphs = [t.get_text(strip=True) for t in tags]
        paragraphs = [p for p in paragraphs if p]

        

        full_text = "\n".join(paragraphs)

        skill_headers = ["Preferred Skills", "Required Skills", "Skills Required", "Key Skills"]
        stop_headers = ["Educational Qualification", "Salary", "Education", "Qualification", "How to Apply", "Job Summary"]

        capturing = False
        skill_lines = []

        for p in paragraphs:
            if any(h in p for h in skill_headers) and len(p) < 40:
                capturing = True
                continue
            if any(h in p for h in stop_headers) and len(p) < 40:
                capturing = False
            if capturing:
                skill_lines.append(p)

        skills_text = ", ".join(skill_lines)

        return full_text, skills_text

    def run(self):
        driver = get_driver()
        jobs = []

        try:
            list_html = self.fetch(driver, self.url, 'div#job-list table')
            jobs = self.parse_list(list_html)

            for job in jobs:
                try:
                    detail_html = self.fetch(driver, job["url"], "main")
                    description, skills = self.parse_detail(detail_html)
                    job["description"] = description
                    job["skills"] = skills
                except Exception:
                    job["description"] = ""
                    job["skills"] = ""
        finally:
            driver.quit()

        return jobs
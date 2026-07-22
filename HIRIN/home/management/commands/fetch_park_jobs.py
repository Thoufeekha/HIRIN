from django.core.management.base import BaseCommand
from home.scraper import TechnoparkScraper, InfoparkScraper
from accounts.models import Job


class Command(BaseCommand):
    help = "Scrape jobs from Technopark and Infopark"

    def handle(self, *args, **options):
        scrapers = [TechnoparkScraper(), InfoparkScraper()]

        total_saved = 0

        for scraper in scrapers:
            self.stdout.write(f"Scraping {scraper.source_name}...")

            try:
                jobs = scraper.run()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{scraper.source_name} failed: {e}"))
                continue

            for j in jobs:
                job, created = Job.objects.update_or_create(
                    source_url=j["url"],
                    defaults={
                        "source": scraper.source_name,
                        "scraped_company_name": j["company"],
                        "title": j["title"],
                        "location": j.get("location", ""),
                        "description": j.get("description", ""),
                        "skills": j.get("skills", ""),
                        "valid_until": j["valid_until"],
                        "is_published": True,
                        "is_closed": False,
                    }
                )
                total_saved += 1

            self.stdout.write(self.style.SUCCESS(f"{scraper.source_name}: {len(jobs)} jobs"))

        self.stdout.write(self.style.SUCCESS(f"Total saved: {total_saved}"))
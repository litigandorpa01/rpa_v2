import asyncio
from app.services.scraper.tyba_scraper import TybaScraper

if __name__ == "__main__":
    process_code = "05001418900120240119200"
    scraper = TybaScraper(
        process_id=process_code,
        captcha_type="recaptcha_v3"
    )
    asyncio.run(scraper.run())

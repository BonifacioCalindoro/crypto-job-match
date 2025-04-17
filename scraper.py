import asyncio
import re
from playwright.async_api import Playwright, async_playwright, expect
from pydantic import BaseModel
from typing import List, Optional
import json

class Job(BaseModel):
    title: str
    company: str
    salary: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    posted: str = ""
    description: str = ""
    link: str = ""

def split_camel_case(text: str) -> List[str]:
    "This function splits a string into a list of words based on camel case"
    return re.findall(r'[A-Z][a-z]*', text)
    
async def run_scraper(playwright: Playwright) -> None:
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://cryptojobslist.com/jobs-new-york?sort=recent")
    await expect(page).to_have_title(re.compile("Web3 & Crypto Jobs"))
    table = page.locator("xpath=/html/body/div/main/section[1]/section/table")
    rows = await (table.locator("xpath=//tr")).all()
    
    jobs = []
    for row in rows[2:]:
        lines = (await row.inner_text()).split('\n')
        location_field = lines[3]
        link = 'https://cryptojobslist.com' + (await (await (row.locator("xpath=//a")).all())[0].get_attribute("href"))
        await row.hover()
        await asyncio.sleep(0.5)
        await row.click()
        await asyncio.sleep(0.5)
        
        # Looking for "Web3" which seems to be a common pattern where tags start
        tag_separator = "Web3"
        if tag_separator in location_field:
            parts = location_field.split(tag_separator)
            clean_location = parts[0].strip()
            # Add Web3 back since it's a tag
            camel_case_part = tag_separator + parts[1]
        else:
            # For lines that might not follow the pattern, try to identify the first camel case word
            match = re.search(r'^(.*?)([A-Z][a-z]+)', location_field)
            if match and match.group(1).strip():
                clean_location = match.group(1).strip()
                camel_case_part = location_field[len(clean_location):]
            else:
                # Fallback: if remote job with no location
                if "Remote" in location_field:
                    clean_location = "Remote"
                    camel_case_part = location_field
                else:
                    clean_location = ""
                    camel_case_part = location_field
        
        # Extract tags using the split_camel_case function
        tags = split_camel_case(camel_case_part)
        
        jobs.append(Job(
            title=lines[0],
            company=lines[1],
            salary=lines[2],
            location=clean_location,
            tags=tags,
            posted=lines[4],
            description=await page.locator('xpath=/html/body/div/main/section[1]/div/div[2]/div[1]').inner_text(),
            link=link
        ))
    json.dump([job.model_dump() for job in jobs], open('jobs.json', 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

    
    # ---------------------
    await context.close()
    await browser.close()
    
    return jobs


async def scrape_jobs() -> None:
    async with async_playwright() as playwright:
        return await run_scraper(playwright)


if __name__ == "__main__":
    asyncio.run(scrape_jobs())


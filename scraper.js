const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

/**
 * Deep LinkedIn Scraper & Job Searcher
 */
async function scrapeLinkedInProfile(url) {
    console.log(`🕵️  Scraping Profile: ${url}`);
    const browser = await puppeteer.connect({ browserWSEndpoint: 'ws://127.0.0.1:18792/cdp' });
    const page = await browser.newPage();
    
    try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 4000));

        const data = await page.evaluate(() => ({
            name: document.querySelector('h1')?.innerText,
            headline: document.querySelector('.text-body-medium')?.innerText,
            experience: Array.from(document.querySelectorAll('section')).find(s => s.innerText.includes('Experience'))
                         ?.innerText.substring(0, 1000)
        }));
        
        await page.close();
        await browser.disconnect();
        return data;
    } catch (e) {
        await page.close();
        await browser.disconnect();
        throw e;
    }
}

async function searchLinkedInJobs(keywords, location = "Paris") {
    console.log(`🔍 Searching Jobs for: ${keywords} in ${location}`);
    const browser = await puppeteer.connect({ browserWSEndpoint: 'ws://127.0.0.1:18792/cdp' });
    const page = await browser.newPage();
    
    try {
        const searchUrl = `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(keywords)}&location=${encodeURIComponent(location)}&f_TPR=r86400`;
        await page.goto(searchUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await new Promise(r => setTimeout(r, 5000));

        const jobs = await page.evaluate(() => {
            const items = [];
            const cards = document.querySelectorAll('.job-card-container, .jobs-search-results__list-item');
            cards.forEach((card, i) => {
                if (i > 4) return; // Limit to top 5 live results
                const title = card.querySelector('h3, .job-card-list__title')?.innerText.trim();
                const company = card.querySelector('.job-card-container__company-name, .job-card-container__primary-description')?.innerText.trim();
                const link = card.querySelector('a')?.href;
                if (title && company) items.push({ title, company, url: link });
            });
            return items;
        });

        await page.close();
        await browser.disconnect();
        return jobs;
    } catch (e) {
        await page.close();
        await browser.disconnect();
        throw e;
    }
}

module.exports = { scrapeLinkedInProfile, searchLinkedInJobs };

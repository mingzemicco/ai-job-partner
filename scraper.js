const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

/**
 * Deep LinkedIn Scraper for ClawHunter
 * Uses the local OpenClaw Browser Relay
 */
async function scrapeLinkedInProfile(url) {
    console.log(`🕵️  Agent starting deep scrape for: ${url}`);
    
    let browser;
    try {
        browser = await puppeteer.connect({
            browserWSEndpoint: 'ws://127.0.0.1:18792/cdp',
        });

        const pages = await browser.pages();
        // Try to find if the tab is already open, otherwise open new
        let page = pages.find(p => p.url().includes(url));
        
        if (!page) {
            console.log('Opening new tab for profile...');
            page = await browser.newPage();
            await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
            // Human-like wait for dynamic content
            await new Promise(r => setTimeout(r, 5000));
        }

        console.log('Extracting structured experience...');
        
        const profileData = await page.evaluate(() => {
            const getElText = (sel) => document.querySelector(sel)?.innerText?.trim();
            
            // Extract Experience Section
            const experience = [];
            const expSection = Array.from(document.querySelectorAll('section')).find(s => s.innerText.includes('Experience'));
            
            if (expSection) {
                const items = expSection.querySelectorAll('li.artdeco-list__item');
                items.forEach(li => {
                    const title = li.querySelector('div.display-flex.align-items-center span[aria-hidden="true"]')?.innerText;
                    const company = li.querySelector('span.t-14.t-normal span[aria-hidden="true"]')?.innerText;
                    const description = li.querySelector('.inline-show-more-text')?.innerText;
                    if (title && company) {
                        experience.push({ title, company, description });
                    }
                });
            }

            return {
                name: getElText('h1'),
                headline: getElText('.text-body-medium'),
                location: getElText('.text-body-small.inline.t-black--light'),
                experience: experience,
                skills: Array.from(document.querySelectorAll('.pvs-list__item-no-padding-with-list-item-margin span[aria-hidden="true"]'))
                            .map(s => s.innerText).slice(0, 10)
            };
        });

        await browser.disconnect();
        return profileData;

    } catch (error) {
        console.error('Scraping failed:', error.message);
        if (browser) await browser.disconnect();
        throw error;
    }
}

// If run directly
if (require.main === module) {
    const targetUrl = process.argv[2];
    if (!targetUrl) {
        console.log('Usage: node scraper.js <linkedin_url>');
        process.exit(1);
    }
    scrapeLinkedInProfile(targetUrl).then(data => {
        console.log('--- EXTRACTED DATA ---');
        console.log(JSON.stringify(data, null, 2));
    });
}

module.exports = { scrapeLinkedInProfile };

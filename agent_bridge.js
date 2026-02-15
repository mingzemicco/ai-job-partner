/**
 * ClawHunter Agent Bridge v2 - Full Loop
 */
const { scrapeLinkedInProfile, searchLinkedInJobs } = require('./scraper.js');
const axios = require('axios');

const RAILWAY_URL = 'https://ai-job-partner-production.up.railway.app';
const POLL_INTERVAL = 4000;

async function agentLoop() {
    console.log('🤖 ClawHunter Agent v2 (Full Loop) is active...');
    
    while (true) {
        try {
            const resp = await axios.get(`${RAILWAY_URL}/api/tasks/pending`);
            const tasks = resp.data;

            for (const taskId in tasks) {
                const url = tasks[taskId];
                console.log(`🚀 Processing Magic Match for: ${url}`);
                
                try {
                    // STEP 1: Scrape Profile
                    const profile = await scrapeLinkedInProfile(url);
                    
                    // STEP 2: Logic - Determine search keywords from profile
                    // (In v3, we can ask AI for these, but for speed we extract from headline)
                    const keywords = profile.headline ? profile.headline.split('|')[0].trim() : "Product Manager";
                    
                    // STEP 3: Search Live Jobs
                    const liveJobs = await searchLinkedInJobs(keywords);
                    
                    // STEP 4: Deliver everything back to Cloud
                    await axios.post(`${RAILWAY_URL}/api/tasks/complete/${taskId}`, {
                        profile: profile,
                        live_jobs: liveJobs
                    });
                    
                    console.log(`✅ Magic Match complete for ${taskId}`);
                } catch (err) {
                    console.error(`❌ Task ${taskId} failed:`, err.message);
                }
            }
        } catch (e) {
            // Silence polling errors
        }
        await new Promise(r => setTimeout(r, POLL_INTERVAL));
    }
}

agentLoop();

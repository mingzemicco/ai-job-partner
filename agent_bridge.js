/**
 * ClawHunter Local Agent Loop
 * Runs on your MacBook to bridge the gap between Cloud (Railway) and Local Browser.
 */
const { scrapeLinkedInProfile } = require('./scraper.js');
const axios = require('axios');

const RAILWAY_URL = 'https://ai-job-partner-production.up.railway.app'; // Update if needed
const POLL_INTERVAL = 5000; // 5 seconds

async function agentLoop() {
    console.log('🤖 ClawHunter Agent is listening for Magic Match requests...');
    
    while (true) {
        try {
            // 1. Check for pending tasks from Railway
            const resp = await axios.get(`${RAILWAY_URL}/api/tasks/pending`);
            const tasks = resp.data;
            const taskIds = Object.keys(tasks);

            if (taskIds.length > 0) {
                for (const taskId of taskIds) {
                    const url = tasks[taskId];
                    console.log(`🚀 New task received! Scraping: ${url}`);
                    
                    try {
                        // 2. Perform the scrape using local relay
                        const profileData = await scrapeLinkedInProfile(url);
                        
                        // 3. Post data back to Railway
                        await axios.post(`${RAILWAY_URL}/api/tasks/complete/${taskId}`, profileData);
                        console.log(`✅ Task ${taskId} completed and delivered.`);
                    } catch (scrapeError) {
                        console.error(`❌ Scraping failed for task ${taskId}:`, scrapeError.message);
                    }
                }
            }
        } catch (error) {
            console.error('📡 Connection error to Railway:', error.message);
        }

        await new Promise(r => setTimeout(r, POLL_INTERVAL));
    }
}

agentLoop();

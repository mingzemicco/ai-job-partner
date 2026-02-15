import json

def extract_linkedin_profile(browser_tool, target_id):
    """
    Uses the OpenClaw browser tool to extract experience from a LinkedIn profile.
    Requires the tab to be connected.
    """
    print(f"Attempting to extract profile from tab {target_id}...")
    
    # We use a combination of snapshots and tailored JavaScript evaluation
    # to bypass LinkedIn's complex DOM.
    
    extraction_script = """
    () => {
        const experience = [];
        const items = document.querySelectorAll('#experience-section + .pvs-list__paged-list-item, section > div#experience ~ ul > li');
        
        // Alternative selector for modern LinkedIn layout
        const sections = document.querySelectorAll('section');
        let expSection = null;
        for (const s of sections) {
            if (s.innerText.includes('Experience') && s.querySelector('ul')) {
                expSection = s;
                break;
            }
        }

        if (expSection) {
            const listItems = expSection.querySelectorAll('li.artdeco-list__item');
            listItems.forEach(li => {
                const title = li.querySelector('div.display-flex.align-items-center span[aria-hidden="true"]')?.innerText;
                const company = li.querySelector('span.t-14.t-normal span[aria-hidden="true"]')?.innerText;
                const dateRange = li.querySelector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]')?.innerText;
                const description = li.querySelector('div.inline-show-more-text')?.innerText;
                
                if (title && company) {
                    experience.push({ title, company, dateRange, description });
                }
            });
        }
        
        return {
            name: document.querySelector('h1')?.innerText,
            headline: document.querySelector('.text-body-medium')?.innerText,
            location: document.querySelector('.text-body-small.inline.t-black--light')?.innerText,
            experience: experience
        };
    }
    """
    
    try:
        # We'll use the browser act tool to run this JS
        # Note: browser.act supports 'eval' kind of requests in some implementations
        # or we can use the snapshot to get the text directly if JS is risky.
        
        # For simplicity and robustness in this environment, let's pull a full snapshot 
        # and use the LLM to parse it, as LinkedIn's class names change frequently.
        
        snapshot = browser_tool(action="snapshot", targetId=target_id)
        return snapshot
    except Exception as e:
        print(f"Extraction error: {e}")
        return None

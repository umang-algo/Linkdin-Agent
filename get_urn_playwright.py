import asyncio
from playwright.async_api import async_playwright
import os
import re

async def get_linkedin_urn():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to your LinkedIn profile...")
        # Since the profile is public, we can just fetch the HTML without logging in
        response = await page.goto('https://www.linkedin.com/in/umang-yadav/')
        
        # Wait a moment for it to load
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        
        # Look for urn:li:member:123456789
        match = re.search(r'urn:li:member:(\d+)', content)
        
        if match:
            urn = match.group(0)
            member_id = match.group(1)
            print(f"\n✅ FOUND IT! Your numeric Member ID is: {member_id}")
            print(f"Your full URN for the .env file is: urn:li:person:{member_id}")
            
            # Auto-update the .env file
            with open('.env', 'r') as file:
                env_content = file.read()
                
            env_content = re.sub(
                r'LINKEDIN_PERSON_URN=.*', 
                f'LINKEDIN_PERSON_URN=urn:li:person:{member_id}', 
                env_content
            )
            
            with open('.env', 'w') as file:
                file.write(env_content)
                
            print("✅ I have successfully updated your .env file with the URN!")
        else:
            print("❌ Could not find the URN in the public profile page. LinkedIn might be blocking public viewing of your profile.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(get_linkedin_urn())

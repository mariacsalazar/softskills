import json
import requests
from bs4 import BeautifulSoup

# Step 1: Convert job_listing.txt to JSON format
def txt_to_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    job_listings = []
    listings = content.split('--------------------------------------------------')

    for listing in listings:
        if listing.strip():
            lines = listing.strip().split('\n')
            job = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    job[key.strip()] = value.strip()
            job_listings.append(job)

    return job_listings

# Step 2: Fetch job description from the link
def fetch_job_description(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        description = soup.select_one('section.adp-body')
        if description:
            return description.get_text(strip=True)
    except Exception as e:
        print(f"Error fetching description for {url}: {str(e)}")
    return None

# Main process
def main():
    # Convert txt to JSON
    job_listings = txt_to_json('job_listing_design_France.txt')

    # Fetch job descriptions and add to JSON
    for job in job_listings:
        if 'Job Link' in job:
            description = fetch_job_description(job['Job Link'])
            if description:
                job['Job Description'] = description

    # Save updated JSON
    with open('job_listings.json', 'w', encoding='utf-8') as f:
        json.dump(job_listings, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

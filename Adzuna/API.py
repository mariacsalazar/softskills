import requests
from datetime import datetime

# Replace with your Adzuna APP ID and APP KEY
app_id = '99f87bd8'
app_key = '4c2fefb1de23090786e0ca6c2f47d585'	

# Define base URL
base_url = 'https://api.adzuna.com/v1/api/jobs/fr/search/'

# Define search keyword and location
search_keyword = 'design'
search_location = 'France'

# Define API parameters
params = {
    'app_id': app_id,
    'app_key': app_key,
    'results_per_page': 50,  # Maximum 50 results per page
    'what': search_keyword,
    'where': search_location,
    'max_days_old': 30,  # Limit to jobs posted in the last 30 days
    'sort_by': 'date'  # Sort by date
}

# Get two pages of data
all_jobs = []
for page in range(1, 3):
    response = requests.get(base_url + str(page), params=params)
    if response.status_code == 200:
        all_jobs.extend(response.json()['results'])
    else:
        print(f"Failed to request page {page}, status code: {response.status_code}")

# Generate filename (using search keyword and location)
filename = f"job_listing_{search_keyword.replace(' ', '_')}_{search_location}.txt"

# Write results to file
with open(filename, 'w', encoding='utf-8') as f:
    for job in all_jobs:
        f.write(f"Job Title: {job.get('title', 'N/A')}\n")
        f.write(f"Company: {job.get('company', {}).get('display_name', 'N/A')}\n")
        f.write(f"Location: {job.get('location', {}).get('display_name', 'N/A')}\n")
        f.write(f"Salary: {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')}\n")
        f.write(f"Posting Date: {job.get('created', 'N/A')}\n")
        f.write(f"Job Link: {job.get('redirect_url', 'N/A')}\n")
        f.write("-" * 50 + "\n")

print(f"Total of {len(all_jobs)} job listings retrieved, saved to {filename}")

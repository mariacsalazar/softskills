We can apply API data collection on this website.




# Adzuna API Job Search Guide

## Step 1: Define Search Keyword and Location in `API.py`

In the `API.py` file, set the job search keyword and location. Example code:

```python
# API.py

# Define search keyword and location 
search_keyword = 'design'
search_location = 'France'

# Set API request URL and query parameters (omitted)
```

## Step 2: Run `API.py` to Get Job Listings

Run the `API.py` file, which will send a request to the Adzuna API and retrieve job data. The results will be saved in the file `job_listing_design_France.txt`, but this part of the data will not contain detailed job information.

## Step 3: Run `script.py` to Scrape Job Details

Next, run the `script.py` file, which will read the job listings from `job_listing_design_France.txt`, extract detailed information for each job, and save the complete data in JSON format as `job_listings.json`.

## Overall Process Summary

1. **Define Search Keyword and Location**:
   - In `API.py`, set `search_keyword` to `'design'` and `search_location` to `'France'`.

2. **Get Job Listings**:
   - Run `API.py` to generate a file `job_listing_design_France.txt` containing the job listings (without detailed information).

3. **Scrape Job Details**:
   - Run `script.py` to read `job_listing_design_France.txt`, obtain complete job details, and save the final results in `job_listings.json`.


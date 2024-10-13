We can apply API data collection on this website.




下面是更新后的指南，包括在运行 `script.py` 前修改 `script.py` 的步骤，采用 Markdown 格式：


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

## Step 3: Modify `script.py` Before Running

Before running `script.py`, modify the following line to ensure the correct file name is used for conversion:

```python
# Convert txt to JSON
job_listings = txt_to_json('job_listing_design_France.txt')
```

## Step 4: Run `script.py` to Scrape Job Details

Now, run the `script.py` file, which will read the job listings from `job_listing_design_France.txt`, extract detailed information for each job, and save the complete data in JSON format as `job_listings.json`.

## Overall Process Summary

1. **Define Search Keyword and Location**:
   - In `API.py`, set `search_keyword` to `'design'` and `search_location` to `'France'`.

2. **Get Job Listings**:
   - Run `API.py` to generate a file `job_listing_design_France.txt` containing the job listings (without detailed information).

3. **Modify `script.py`**:
   - Change the file name in `script.py` to match the output from `API.py`.

4. **Scrape Job Details**:
   - Run `script.py` to read `job_listing_design_France.txt`, obtain complete job details, and save the final results in `job_listings.json`.



# BF4 Cheat Report Scraper

A simple and effective command-line tool to scrape and export Battlefield 4 player statistics from [bf4cheatreport.com](https://bf4cheatreport.com) directly into CSV format.

## Features

* **Easy to use**: Just provide a bf4cheatreport.com URL via the command line.
* **Accurate Data**: Preserves exact column names and order as presented on bf4cheatreport.com.
* **Automatic Filename**: The output CSV is named automatically using the player's username (personaName).
* **Computed Fields**: Automatically computes additional fields like the "spot" value.
* **Timezone-aware**: Correctly formats datetime fields in UTC.

## Requirements

* Python 3.8 or higher
* `requests` library (install via `pip install requests`)

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/bf4-cheat-report-scraper.git
cd bf4-cheat-report-scraper
```

Install required Python dependencies:

```bash
pip install requests
```

## Usage

Run the script from the command line:

```bash
python bf4cr_to_csv.py
```

When prompted, paste your bf4cheatreport.com URL:

```text
Please enter the bf4cheatreport.com URL: https://bf4cheatreport.com/?pid=YOUR_PID&cnt=200&startdate=YOUR_DATE
```

The CSV file will be created in the same directory, named after the player's username.

## Example Output

After execution, you'll see:

```
✅ Done! CSV saved as playername.csv
```

## License

MIT License – feel free to use, modify, and distribute!

# Restaurant-Robot-Data-Collection
---
# YouTube Video Analysis Project

## Overview

This project aims to gather data from sources like YouTube, Reddit, or Twitter, to explain why restaurant robots are less popular in the USA than in countries like Korea, Japan, or China. By analyzing video comments and transcripts, the project seeks to provide insights for the food service industry and policymakers. The application is built using Python and utilizes libraries such as `googleapiclient`, `pandas`, and `langchain_community`. The main functionalities include:
Searching for YouTube videos based on a keyword.
Fetching video details, transcripts, and comments.
Summarizing comments and transcripts using an LLM (Language Learning Model).
Exporting the collected data to Excel for analysis 

## Get Started

### Prerequisites

Ensure you have the following installed on your machine:
- Python 3.7+
- Required Python packages (listed in `requirements.txt`)

### Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install the required packages: 
google-api-python-client
pandas
langchain_community
youtube-transcript-api



### Configuration

Replace the placeholder `api_key` in the script with your actual YouTube Data API key. 

### Running the Code

1. Run the script

2. Follow the prompts to input:
    - The search keyword (underscore in place of spaces)
    - The number of videos to retrieve
    - Whether to remove duplicate videos (Input ‘Y’ for yes and ‘N’ for no)

### Example Usage


Enter Search Keyword: Restaurant_robots
Enter Number of Videos: 10
Do You Want to Remove Duplicate Videos? (Y/N) Y


### Output

The script outputs the following:
- A list of YouTube videos matching the keyword.
- An Excel file `Comment Archive.xlsx` containing video titles, URLs, comments, and comment summaries.
- An Excel file `Transcript Record.xlsx` containing video details (publish date, view count, description), organized transcripts, and transcript summaries.

## General Information on the Code

### Main Functions

- `get_youtube_videos_by_keyword(api_key, keyword, max_results)`: Fetches YouTube videos based on a keyword.
- `get_video_details(api_key, video_id)`: Retrieves detailed information about a specific video.
- `fetch_comments(video_id)`: Fetches comments for a specific video.
- `summarize_comments(comments)`: Summarizes comments using the LLM.
- `get_transcript(video_id)`: Retrieves the transcript of a specific video.
- `organize_transcript(video_id)`: Organizes the transcript text.
- `summarize_transcript(video_id)`: Summarizes the organized transcript.
- `remove_duplicates(video)`: Removes duplicate videos from the list.

### Dependencies

- `googleapiclient`: To interact with the YouTube Data API.
- `pandas`: For data manipulation and exporting to Excel.
- `langchain_community.llms`: To interact with the Language Learning Model (LLM).

### Notes

- Ensure you have a valid YouTube Data API key.
- Adjust the LLM base URL and model as needed.

---
# Reddit Data Collector

This script collects submissions and comments from Reddit using the Pushshift API and PRAW (Python Reddit API Wrapper). The collected data is exported to an Excel file for further analysis.

## Prerequisites

- Python 3.8 or higher
- `praw` library
- `pushshift_py` library
- `typer` library
- `loguru` library
- `codetiming` library
- `pandas` library
- `pyyaml` library
- `pretty_errors` library
- `langchain_community` library

You can install the required libraries using pip:

```bash
pip install praw pushshift_py typer loguru codetiming pandas pyyaml pretty_errors langchain_community
```

## Configuration

1. **Reddit API Credentials**: You need a Reddit client ID, client secret, and username. Obtain these by creating a Reddit app [here](https://www.reddit.com/prefs/apps).

2. **Pushshift API**: No additional configuration is needed for Pushshift API.

## Usage

### Command Line

You can run the script from the command line using `typer`. Below is the syntax to run the script:

```bash
python subreddit_downloader.py [OPTIONS]
```

### Options

- `subreddit`: The name of the subreddit you want to fetch data from.
- `output_dir`: The directory where the data will be saved. Default is `./data`.
- `batch_size`: The number of submissions to fetch per request. Default is `1000`.
- `laps`: The number of times to fetch data. Default is `3`.
- `reddit_id`: Your Reddit client ID.
- `reddit_secret`: Your Reddit client secret.
- `reddit_username`: Your Reddit username.
- `utc_after`: Fetch submissions after this UTC date.
- `utc_before`: Fetch submissions before this UTC date.
- `debug`: Enable debug logging. Default is `False`.
- `comments_cap`: Maximum number of comments to fetch per submission. Default is `100`.

### Example

```bash
python subreddit_downloader.py subreddit_name --output_dir "./reddit_data" --batch_size 500 --laps 2 --reddit_id "your_client_id" --reddit_secret "your_client_secret" --reddit_username "your_username" --utc_after 1609459200 --utc_before 1672531199 --debug True --comments_cap 50
```

## How It Works

1. **Initialization**: The script initializes the Reddit and Pushshift API clients and prepares the directories for storing data.

2. **Data Collection**: For each lap, the script fetches submissions from the specified subreddit within the given UTC range. For each submission, it collects comments up to the specified limit.

3. **Data Storage**: The fetched submissions and comments are stored in JSON files and also aggregated into pandas DataFrames.

4. **Export**: The DataFrames are exported to an Excel file named `RedditArchive.xlsx`, with separate sheets for submissions and comments.

## Directory Structure

After running the script, the directory structure will look like this:

```
output_dir/
└── subreddit_name/
    └── run_id/
        ├── submissions/
        ├── submissions/raw/
        ├── comments/
        ├── comments/raw/
        └── RedditArchive.xlsx
```

## Error Handling

- **NotFound**: If a submission is not found, a warning is logged.
- **General Errors**: Any other errors during the execution will be logged with details.

## License

This script is provided under the MIT License. See the LICENSE file for more details.

## Contributing

Feel free to open issues or pull requests if you have improvements or bug fixes.

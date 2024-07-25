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

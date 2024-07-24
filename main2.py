from googleapiclient.discovery import build
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi as yta
from langchain_community.llms import Ollama

# Initialize the LLM instance and point to the ATR lab server machine
llm = Ollama(base_url="http://131.123.41.132:11434", model="llava:34b")


def get_youtube_videos_by_keyword(api_key, keyword, max_results):
    # Build the YouTube service object
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Call the search.list method to retrieve results matching the specified query term
    search_response = youtube.search().list(
        q=keyword,
        part='id,snippet',
        maxResults=max_results
    ).execute()

    # Extract video details from the search response
    videos = []
    for item in search_response.get('items', []):
        if item['id']['kind'] == 'youtube#video':
            video_data = {
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId'],
                'description': item['snippet']['description'],
                'channelTitle': item['snippet']['channelTitle'],
                'publishedAt': item['snippet']['publishedAt']
            }
            videos.append(video_data)

    return videos


def get_video_details(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()
    item = response['items'][0]
    details = {
        'Title': item['snippet']['title'],
        'Description': item['snippet']['description'],
        'Publish Date': item['snippet']['publishedAt'],
        'View Count': item['statistics']['viewCount'],
        'URL': f"https://www.youtube.com/watch?v={video_id}"
    }
    return details


def get_transcript(video_id):
    try:
        transcript = yta.get_transcript(video_id)
        processed_transcript = ' '.join([val['text'] for val in transcript if 'text' in val])
        return processed_transcript
    except Exception as e:
        print(f"Error getting transcript for video {video_id}: {e}")
        return ""


def organize_transcript(video_id):
    # Get the transcript text
    info = get_transcript(video_id)

    # You can update the prompt to whatever you want
    organize_text = llm.invoke(f"""
                rearrange the following text into a paragraph without losing any words:
                "{info}". 
                """)
    return organize_text

def summarize_transcript(video_id):
    # Get the transcript text
    info = organize_transcript(video_id)

    # You can update the prompt to whatever you want
    summary_text = llm.invoke(f"""
                summarize the following text without losing any important points:
                "{info}". 
                """)
    return summary_text

def remove_duplicates(video):
    new = []
    [new.append(x) for x in video if x not in new]
    return new

# Example usage
api_key = 'AIzaSyBqUI9I6z5br6_v_dC5lxoNsn72BjapSXg'
keyword = input("Enter Search Keyword: ")
num_Videos = input("Enter Number of Videos: ")
duplicates = input("Do You Want to Remove Duplicate Videos? (Y/N) ")
videos = get_youtube_videos_by_keyword(api_key, keyword, num_Videos)
if duplicates == "Y":
    videos = remove_duplicates(videos)


video_details_list = []
count = 1
for video in videos:
    print(video['videoId'])
    print("Videos Processed: " + str(count))
    count += 1
    print("Videos Remaining: " + str(len(videos) - count))
    video_details = get_video_details(api_key, video['videoId'])
    # Add the organized transcript to the video details
    video_details['Transcript'] = organize_transcript(video['videoId'])
    video_details['Transcript Summary'] = summarize_transcript(video['videoId'])
    video_details_list.append(video_details)

# Create a DataFrame with video details
df = pd.DataFrame(video_details_list)

# Define the Excel file name
excel_file = "Transcript Record.xlsx"

# Export the DataFrame to Excel
df.to_excel(excel_file, index=False)
print(f'Video details exported to {excel_file}')


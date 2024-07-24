from googleapiclient.discovery import build
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import pandas as pd
from langchain_community.llms import Ollama

llm = Ollama(base_url="http://131.123.41.132:11434", model="llava:34b")


def get_youtube_videos_by_keyword(api_key, keyword, max_results):
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_response = youtube.search().list(
        q=keyword,
        part='id,snippet',
        maxResults=max_results
    ).execute()

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

def get_video_details(youtube, video_id):
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    return response['items'][0]['snippet']

def extract_keywords(text, num_keywords=12):
    words = word_tokenize(text)
    words = [word.lower() for word in words]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and word not in stop_words]
    most_common = Counter(words).most_common(num_keywords)
    keywords = [word for word, _ in most_common]
    return keywords

def get_video_keywords(youtube, video_id):
    details = get_video_details(youtube, video_id)
    title = details['title']
    description = details['description']
    text = title + ' ' + description
    keywords = extract_keywords(text)
    return keywords


def fetch_comments (video_id):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100  # Set the maximum results per page
    )
    while request:
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        request = youtube.commentThreads().list_next(request, response)  # Use the nextPageToken for pagination
    return comments


def summarize_comments(comments):
    # Get the transcript text
    all_comments = "\n".join(comments)
    # You can update the prompt to whatever you want
    summary_text = llm.invoke(f"""
                summarize the following comments without losing any important points or opinions:
                "{all_comments}".
                """)
    return summary_text

def remove_duplicates(video):
    new = []
    [new.append(x) for x in video if x not in new]
    return new

# Main logic
api_key = 'AIzaSyBqUI9I6z5br6_v_dC5lxoNsn72BjapSXg'  # Replace with your actual YouTube API key
keyword = input("Enter Search Keyword: ")
num_Videos = input("Enter Number of Videos: ")
duplicates = input("Do You Want to Remove Duplicate Videos? (Y/N) ")
videos = get_youtube_videos_by_keyword(api_key, keyword, num_Videos)
count = 1
if duplicates == "Y":
    videos = remove_duplicates(videos)


# nltk.download('punkt')
# nltk.download('stopwords')

youtube = build('youtube', 'v3', developerKey=api_key)

excel_file = "Comment Archive.xlsx"
all_data = []

for video in videos:
    try:
        video_url = "https://www.youtube.com/watch?v=" + video['videoId']
        print(video_url)
        print("Videos Processed: " + str(count))
        count += 1
        print("Videos Remaining: " + str(len(videos) - count))
        comments = fetch_comments(video['videoId'])
        comment_summary = summarize_comments(comments)

        for comment in comments:
            all_data.append({
                'Title': video['title'],
                'URL': video_url,
                'Comments': comment,
                'Comment Summary': comment_summary
            })


    except Exception as e:
        print(f"An error occurred: {e}")
        continue

# Create a DataFrame with all data
final_df = pd.DataFrame(all_data)

# Export to Excel
final_df.to_excel(excel_file, index=False)
print(f'Video information exported to {excel_file}')

import streamlit as st
import requests
from datetime import datetime, timedelta

# =========================
# YouTube API Configuration
# =========================
API_KEY = "AIzaSyC_al158fXsxfZZMV0N8hWKuA_fCTGZIhc"   # <-- yahan apni API key dalen
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# Streamlit UI
# =========================
st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords & time range.")

# Input fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# Keywords list
keywords = [
    "Affair Relationship Stories", "Reddit Update", "Reddit Relationship Advice",
    "Reddit Relationship", "Reddit Cheating", "AITA Update", "Open Marriage",
    "Open Relationship", "X BF Caught", "Stories Cheat", "X GF Reddit",
    "AskReddit Surviving Infidelity", "GurlCan Reddit",
    "Cheating Story Actually Happened", "Cheating Story Real",
    "True Cheating Story", "Reddit Cheating Story", "R/Surviving Infidelity",
    "Surviving Infidelity", "Reddit Marriage", "Wife Cheated I Can't Forgive",
    "Reddit API", "Exposed Wife", "Cheat Exposed"
]

# =========================
# Fetch Button
# =========================
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        all_results = []

        st.info(f"🔎 Searching videos uploaded in the last {days} days...")

        # Loop through keywords and fetch results
        for keyword in keywords:
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY
            }
            response = requests.get(YOUTUBE_SEARCH_URL, params=params)
            data = response.json()

            if "items" in data:
                for item in data["items"]:
                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    channel = item["snippet"]["channelTitle"]
                    publish_date = item["snippet"]["publishedAt"]

                    # Get video statistics
                    video_params = {
                        "part": "statistics",
                        "id": video_id,
                        "key": API_KEY
                    }
                    video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
                    video_data = video_response.json()

                    if "items" in video_data and len(video_data["items"]) > 0:
                        stats = video_data["items"][0]["statistics"]
                        views = stats.get("viewCount", "0")
                        likes = stats.get("likeCount", "0")
                    else:
                        views, likes = "N/A", "N/A"

                    all_results.append({
                        "Keyword": keyword,
                        "Title": title,
                        "Channel": channel,
                        "Published": publish_date,
                        "Views": views,
                        "Likes": likes,
                        "Video URL": f"https://www.youtube.com/watch?v={video_id}"
                    })

        # Show results in table
        if all_results:
            st.success(f"✅ Found {len(all_results)} videos!")
            st.dataframe(all_results)
        else:
            st.warning("No results found for the given period.")

    except Exception as e:
        st.error(f"Error: {e}")

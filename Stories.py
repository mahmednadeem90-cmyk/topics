import streamlit as st
import requests
from datetime import datetime, timedelta

# =========================
# YouTube API Configuration
# =========================
API_KEY = st.secrets["YOUTUBE_API_KEY"]   # <-- yahan apni API key rakho
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# Streamlit UI
# =========================
st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords & time range.")

days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

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

if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        results_count = 0

        st.info(f"🔎 Searching videos uploaded in the last {days} days...")

        for keyword in keywords:
            st.write(f"Searching for keyword: **{keyword}**")

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

            if "items" not in data or len(data["items"]) == 0:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            found_for_keyword = False
            for item in data["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"]
                publish_date = item["snippet"]["publishedAt"]

                video_params = {"part": "statistics", "id": video_id, "key": API_KEY}
                video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
                video_data = video_response.json()

                if "items" in video_data and len(video_data["items"]) > 0:
                    stats = video_data["items"][0]["statistics"]
                    views = stats.get("viewCount", "0")
                    likes = stats.get("likeCount", "0")
                    st.success(f"📹 {title} | {channel} | Views: {views} | Likes: {likes}")
                    results_count += 1
                    found_for_keyword = True
                else:
                    st.warning(f"Failed to fetch video statistics for keyword: {keyword}")

            if not found_for_keyword:
                st.warning(f"No valid videos fetched for keyword: {keyword}")

        # Final summary
        if results_count > 0:
            st.success(f"✅ Found {results_count} results across all keywords!")
        else:
            st.warning("No results found across all keywords.")

    except Exception as e:
        st.error(f"Error: {e}")

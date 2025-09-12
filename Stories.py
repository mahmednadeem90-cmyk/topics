import streamlit as st
import requests
from datetime import datetime, timedelta

# =========================
# YouTube API Configuration
# =========================
API_KEY = "AIzaSyC_al158fXsxfZZMV0N8hWKuA_fCTGZIhc"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# Streamlit UI
# =========================
st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords & time range.")

days = st.number_input(
    "📅 How many past days of videos do you want to search? (1-30)", 
    min_value=1, 
    max_value=30, 
    value=7,
    help="Example: If you enter 7, it will fetch videos uploaded in the last 7 days."
)

max_videos = st.number_input("How many videos per keyword?", min_value=1, max_value=20, value=5)

# =========================
# User enters keywords
# =========================
user_input = st.text_area(
    "✍️ Enter keywords (separate with commas):", 
    placeholder="Example: Affair Relationship Stories, Reddit Update, Cheating Story"
)

# Convert user input into list
if user_input.strip() != "":
    keywords = [kw.strip() for kw in user_input.split(",")]
else:
    keywords = []


if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        total_results = 0

        st.info(f"🔎 Searching videos uploaded in the last {days} days...")

        for keyword in keywords:
            # Expander (folder) for each keyword
            with st.expander(f"📂 {keyword}"):
                params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "publishedAfter": start_date,
                    "maxResults": max_videos,
                    "key": API_KEY
                }
                response = requests.get(YOUTUBE_SEARCH_URL, params=params)
                data = response.json()

                if "items" not in data or len(data["items"]) == 0:
                    st.warning(f"No videos found for keyword: {keyword}")
                    continue

                found_for_keyword = False
                for item in data["items"]:
                    if "videoId" not in item["id"]:
                        continue

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

                        # Show video details inside expander
                        st.write(f"🎬 **{title}**")
                        st.write(f"📺 Channel: {channel}")
                        st.write(f"📅 Published: {publish_date}")
                        st.write(f"👁 Views: {views} | 👍 Likes: {likes}")
                        st.markdown(f"[▶ Watch Video](https://www.youtube.com/watch?v={video_id})")
                        st.divider()

                        total_results += 1
                        found_for_keyword = True
                    else:
                        st.warning(f"Failed to fetch video statistics for: {title}")

                if not found_for_keyword:
                    st.warning(f"No valid videos fetched for keyword: {keyword}")

        if total_results > 0:
            st.success(f"✅ Found {total_results} results across all keywords!")
        else:
            st.warning("No results found across all keywords.")

    
       if all_results:
    # Sorting options
    sort_by = st.radio("Sort videos by:", ["Views", "Likes", "Published Date"])

    # Apply sorting
    if sort_by == "Views":
        all_results = sorted(all_results, key=lambda x: int(x["Views"]), reverse=True)
    elif sort_by == "Likes":
        all_results = sorted(all_results, key=lambda x: int(x["Likes"]), reverse=True)
    elif sort_by == "Published Date":
        all_results = sorted(all_results, key=lambda x: x["Published"], reverse=True)

    # Show results
    st.dataframe(all_results)

    except Exception as e:
        st.error(f"Error: {e}")

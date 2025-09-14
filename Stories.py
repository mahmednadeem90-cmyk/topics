import streamlit as st
import requests
from datetime import datetime, timedelta

# =========================
# YouTube API Configuration
# =========================
API_KEY = "YOUR_API_KEY"   # apni YouTube API key yahan paste karein
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# Streamlit UI
# =========================
st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords & time range.")

# User chooses how many past days
days = st.number_input(
    "📅 How many past days of videos do you want to search? (1-30)", 
    min_value=1, 
    max_value=30, 
    value=7,
    help="Example: If you enter 7, it will fetch videos uploaded in the last 7 days."
)

# User chooses how many videos per keyword
max_videos = st.number_input("🎥 How many videos per keyword?", min_value=1, max_value=20, value=5)

# User enters keywords
user_input = st.text_area(
    "✍️ Enter keywords (separate with commas):", 
    placeholder="Example: Affair Relationship Stories, Reddit Update, Cheating Story"
)

# Convert input into list
keywords = [kw.strip() for kw in user_input.split(",") if kw.strip()]

# =========================
# Fetch Data Button
# =========================
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        total_results = 0
        all_results = []

        st.info(f"🔎 Searching videos uploaded in the last {days} days...")

        for keyword in keywords:
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

                for item in data["items"]:
                    if "videoId" not in item["id"]:
                        continue

                    video_id = item["id"]["videoId"]
                    title = item["snippet"]["title"]
                    channel = item["snippet"]["channelTitle"]
                    publish_date = item["snippet"]["publishedAt"]

                    # Fetch video statistics
                    video_params = {"part": "statistics", "id": video_id, "key": API_KEY}
                    video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
                    video_data = video_response.json()

                    if "items" in video_data and len(video_data["items"]) > 0:
                        stats = video_data["items"][0]["statistics"]
                        views = stats.get("viewCount", "0")
                        likes = stats.get("likeCount", "0")

                        # Show video details
                        st.write(f"🎬 **{title}**")
                        st.write(f"📺 Channel: {channel}")
                        st.write(f"📅 Published: {publish_date}")
                        st.write(f"👁 Views: {views} | 👍 Likes: {likes}")
                        st.markdown(f"[▶ Watch Video](https://www.youtube.com/watch?v={video_id})")
                        st.divider()

                        all_results.append({
                            "Keyword": keyword,
                            "Title": title,
                            "Channel": channel,
                            "Published": publish_date,
                            "Views": views,
                            "Likes": likes,
                            "Video URL": f"https://www.youtube.com/watch?v={video_id}"
                        })

                        total_results += 1
                    else:
                        st.warning(f"⚠️ Failed to fetch statistics for: {title}")

        # Save results in session_state
        if total_results > 0:
            st.session_state["all_results"] = all_results
            st.session_state["total_results"] = total_results
            st.success(f"✅ Found {total_results} results across all keywords!")
        else:
            st.warning("No results found across all keywords.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# =========================
# Sorting Section (always visible after fetch)
# =========================
if "all_results" in st.session_state and len(st.session_state["all_results"]) > 0:
    sort_by = st.radio("📊 Sort videos by:", ["Views", "Likes", "Published Date"])

    results = st.session_state["all_results"]

    if sort_by == "Views":
        results = sorted(results, key=lambda x: int(x["Views"]), reverse=True)
    elif sort_by == "Likes":
        results = sorted(results, key=lambda x: int(x["Likes"]), reverse=True)
    elif sort_by == "Published Date":
        results = sorted(results, key=lambda x: x["Published"], reverse=True)

    st.dataframe(results)

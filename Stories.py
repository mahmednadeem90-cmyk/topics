import streamlit as st
import requests
from datetime import datetime, timedelta

# =========================
# YouTube API Configuration
# =========================
API_KEY = "YOUR_API_KEY"   # apni YouTube Data API key yahan daalein
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# =========================
# Theme Toggle (Light/Dark)
# =========================
mode = st.radio("🌗 Select Mode:", ["Day Mode", "Night Mode"])
if mode == "Night Mode":
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stExpander {
            background-color: #262730;
            color: #fafafa;
        }
        .stDataFrame, .stMarkdown, .stRadio, .stText, .stNumberInput {
            color: #fafafa !important;
        }
        .css-1d391kg, .css-10trblm, .css-16huue1, .css-qrbaxs {
            color: #fafafa !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Streamlit UI
# =========================
st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords, country & time range.")

# Days filter
days = st.number_input(
    "📅 How many past days of videos do you want to search? (1-30)", 
    min_value=1, 
    max_value=30, 
    value=7
)

# Max videos filter
max_videos = st.number_input(
    "How many videos per keyword?", 
    min_value=1, 
    max_value=20, 
    value=5
)

# Country filter
country = st.text_input(
    "🌍 Enter Country Code (example: US, IN, PK, GB):", 
    value="US",
    help="Use 2-letter ISO country codes (e.g., US=United States, IN=India, PK=Pakistan, GB=United Kingdom)"
)

# Keywords input
user_input = st.text_area(
    "✍️ Enter keywords (separate with commas):", 
    placeholder="Example: Affair Relationship Stories, Reddit Update, Cheating Story"
)

# Convert user input into list
keywords = [kw.strip() for kw in user_input.split(",")] if user_input.strip() else []

# =========================
# Fetch Button
# =========================
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        total_results = 0
        all_results = []

        st.info(f"🔎 Searching videos uploaded in the last {days} days for country: {country}...")

        for keyword in keywords:
            with st.expander(f"📂 {keyword}"):
                params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "publishedAfter": start_date,
                    "maxResults": max_videos,
                    "regionCode": country,   # ✅ Country filter added
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

        # Sorting and Summary
        if total_results > 0:
            st.success(f"✅ Found {total_results} results across all keywords in {country}!")

            sort_by = st.radio("Sort videos by:", ["Views", "Likes", "Published Date"])

            if sort_by == "Views":
                all_results = sorted(all_results, key=lambda x: int(x["Views"]), reverse=True)
            elif sort_by == "Likes":
                all_results = sorted(all_results, key=lambda x: int(x["Likes"]), reverse=True)
            elif sort_by == "Published Date":
                all_results = sorted(all_results, key=lambda x: x["Published"], reverse=True)

            st.dataframe(all_results)
        else:
            st.warning(f"No results found for {country}.")

    except Exception as e:
        st.error(f"Error: {e}")

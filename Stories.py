import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# YouTube API Configuration
# =========================
API_KEY = "AIzaSyC_al158fXsxfZZMV0N8hWKuA_fCTGZIhc"   # <-- apni API key yahan paste karein
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="🔥 YouTube Viral Topics Tool", layout="wide")

# Light / Dark Mode
theme = st.radio("🎨 Choose Theme:", ["Light", "Dark"], horizontal=True)
if theme == "Dark":
    st.markdown(
        """
        <style>
        body { background-color: #121212; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("🔥 YouTube Viral Topics Tool")
st.write("Find viral YouTube videos based on keywords, filters, and charts.")

# =========================
# User Inputs
# =========================
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("📅 From Date:", datetime.utcnow() - timedelta(days=7))
with col2:
    end_date = st.date_input("📅 To Date:", datetime.utcnow())

max_videos = st.number_input("🎥 How many videos per keyword?", min_value=1, max_value=20, value=5)

user_input = st.text_area(
    "✍️ Enter keywords (separate with commas):", 
    placeholder="Example: Affair Relationship Stories, Reddit Update, Cheating Story"
)
keywords = [kw.strip() for kw in user_input.split(",") if kw.strip()]

# Filters
min_views = st.number_input("👁 Minimum Views:", min_value=0, value=0)
min_likes = st.number_input("👍 Minimum Likes:", min_value=0, value=0)

# =========================
# Fetch Data
# =========================
if st.button("Fetch Data"):
    try:
        all_results = []
        total_results = 0

        st.info(f"🔎 Searching videos from {start_date} to {end_date}...")

        for keyword in keywords:
            with st.expander(f"📂 {keyword}"):
                params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "publishedAfter": datetime.combine(start_date, datetime.min.time()).isoformat("T") + "Z",
                    "publishedBefore": datetime.combine(end_date, datetime.max.time()).isoformat("T") + "Z",
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
                    thumbnail = item["snippet"]["thumbnails"]["default"]["url"]

                    # Video statistics
                    video_params = {"part": "statistics", "id": video_id, "key": API_KEY}
                    video_response = requests.get(YOUTUBE_VIDEO_URL, params=video_params)
                    video_data = video_response.json()

                    views, likes = 0, 0
                    if "items" in video_data and len(video_data["items"]) > 0:
                        stats = video_data["items"][0]["statistics"]
                        views = int(stats.get("viewCount", 0))
                        likes = int(stats.get("likeCount", 0))

                    # Apply filters
                    if views < min_views or likes < min_likes:
                        continue

                    # Show video details
                    st.image(thumbnail, width=120)
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

        # Save results
        if total_results > 0:
            st.session_state["all_results"] = all_results
            st.session_state["total_results"] = total_results
            st.success(f"✅ Found {total_results} results across all keywords!")
        else:
            st.warning("No results found across all keywords.")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# =========================
# Sorting + Download + Charts
# =========================
if "all_results" in st.session_state and len(st.session_state["all_results"]) > 0:
    results = st.session_state["all_results"]

    # Sorting
    sort_by = st.radio("📊 Sort videos by:", ["Views", "Likes", "Published Date"])
    if sort_by == "Views":
        results = sorted(results, key=lambda x: x["Views"], reverse=True)
    elif sort_by == "Likes":
        results = sorted(results, key=lambda x: x["Likes"], reverse=True)
    elif sort_by == "Published Date":
        results = sorted(results, key=lambda x: x["Published"], reverse=True)

    df = pd.DataFrame(results)
    st.dataframe(df)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Results as CSV",
        csv,
        "youtube_results.csv",
        "text/csv",
        key="download-csv"
    )

    # Charts
    st.subheader("📈 Analytics")
    fig, ax = plt.subplots()
    df.groupby("Keyword")["Views"].sum().plot(kind="bar", ax=ax)
    plt.ylabel("Total Views")
    plt.title("Total Views per Keyword")
    st.pyplot(fig)

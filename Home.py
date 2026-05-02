import pandas as pd
import streamlit as st
from streamlit import sidebar
from streamlit_option_menu import option_menu
import plotly.express as px

st.set_page_config(page_title="SPOTIFY", layout="wide")

# load data set

df = pd.read_csv("SPOTIFY.csv")

with sidebar:
    select = option_menu("Spotify Dashboard",
                         options=["Overview", "Song Analysis", "Artist Analysis", "Genre Analysis", "Streaming Status",
                                  "Dataset View"],
                         icons=["house", "music-note", "person", "collection", "bar-chart", "table"],
                         default_index=0
                         )
if select == "Overview":
    st.title("🚀 Spotify Dataset Overview")

    # Ensure Date is in datetime format with mixed format support
    df["release_date"] = pd.to_datetime(df["release_date"], errors='coerce', format='mixed')
    df["release_year"] = df["release_date"].dt.year

    total_songs = df.shape[0]
    total_artists = df["artist"].nunique()
    total_albums = df["album"].nunique()
    total_genres = df["genre"].nunique()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Total Songs", f"{total_songs:,}")
    kpi2.metric("Total Artists", f"{total_artists:,}")
    kpi3.metric("Total Albums", f"{total_albums:,}")
    kpi4.metric("Total Genres", f"{total_genres:,}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Releases Trend over Time")
        releases_by_year = df.groupby("release_year").size().reset_index(name="count")
        fig_trend = px.line(
            releases_by_year,
            x="release_year",
            y="count",
            title="Number of Songs Released per Year",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#1DB954"]  # Spotify Green
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_right:
        st.subheader("🔥 Genre vs Popularity Heatmap")
        genre_pop = df.groupby("genre")["popularity"].mean().sort_values(ascending=False).reset_index()
        fig_heat = px.bar(
            genre_pop,
            x="popularity",
            y="genre",
            orientation='h',
            title="Average Popularity by Genre",
            color="popularity",
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

if select == "Song Analysis":
    st.title("Song Analysis")

    st.subheader("Total Song In Database")

    total_songs = df.shape[0]
    avg_popularity = round(df["popularity"].mean(), 2)
    total_streams = df["stream"].sum()
    avg_duration = round(df["duration"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Songs", total_songs)
    col2.metric("Average Popularity", avg_popularity)
    col3.metric("Total Streams", total_streams)
    col4.metric("Avg Duration (sec)", avg_duration)

    st.divider()

    st.subheader("Top 10 Popular Songs")

    top_songs = df.sort_values(by="popularity", ascending=False).head(10)

    fig1 = px.bar(
        top_songs,
        x="song_title",
        y="popularity",
        color="artist",
        title="Top 10 Popular Songs"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Song Popularity Distribution")

    fig2 = px.histogram(
        df,
        x="popularity",
        nbins=10,
        title="Popularity Distribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

if select == "Artist Analysis":
    st.title("👨‍🎤 Artist Analysis")

    artist_list = sorted(df["artist"].unique())
    selected_artist = st.selectbox("Select an Artist for Deep Dive", artist_list)

    artist_data = df[df["artist"] == selected_artist]

    # Artist KPIs
    total_artist_songs = artist_data.shape[0]
    total_artist_streams = artist_data["stream"].sum()
    avg_artist_popularity = round(artist_data["popularity"].mean(), 2)
    most_common_genre = artist_data["genre"].mode()[0] if not artist_data.empty else "N/A"

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Songs", total_artist_songs)
    kpi2.metric("Total Streams", f"{total_artist_streams:,}")
    kpi3.metric("Avg Popularity", avg_artist_popularity)
    kpi4.metric("Primary Genre", most_common_genre)

    st.divider()

    col_top_left, col_top_right = st.columns(2)

    with col_top_left:
        st.subheader(f"Top Songs by {selected_artist}")
        top_artist_songs = artist_data.nlargest(10, "stream")
        fig_artist_songs = px.bar(
            top_artist_songs,
            x="stream",
            y="song_title",
            orientation='h',
            title=f"Top 10 Songs by {selected_artist}",
            color="popularity",
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_artist_songs, use_container_width=True)

    with col_top_right:
        st.subheader("Album Distribution")
        album_counts = artist_data["album"].value_counts().reset_index()
        album_counts.columns = ["album", "song_count"]
        fig_albums = px.pie(
            album_counts,
            values="song_count",
            names="album",
            title=f"Songs per Album for {selected_artist}",
            hole=0.4
        )
        st.plotly_chart(fig_albums, use_container_width=True)

    st.divider()

    # Comparison Section
    st.subheader("Artist Comparison (Top 10 by Total Streams)")
    top_10_artists = df.groupby("artist")["stream"].sum().nlargest(10).reset_index()
    fig_compare = px.bar(
        top_10_artists,
        x="artist",
        y="stream",
        title="Top 10 Artists by Total Streams",
        color="stream",
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    st.subheader("Artist Productivity vs. Popularity")
    artist_stats = df.groupby("artist").agg({
        "song_title": "count",
        "popularity": "mean",
        "stream": "sum"
    }).reset_index()
    artist_stats.columns = ["artist", "song_count", "avg_popularity", "total_streams"]

    fig_scatter = px.scatter(
        artist_stats,
        x="song_count",
        y="avg_popularity",
        size="total_streams",
        hover_name="artist",
        title="Artist Song Count vs. Avg Popularity (Size by Streams)",
        labels={"song_count": "Number of Songs", "avg_popularity": "Average Popularity"},
        template="plotly_dark"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


if select == "Genre Analysis":

    st.title("Genre Analysis")

    st.subheader("Genre Distribution")

    genre= df['genre'].value_counts()

    fig1 = px.pie(
            genre,
            values=genre.values,
            names=genre.index,
            title="Songs Distribution by Genre"
    )

    st.plotly_chart(fig1, use_container_width=True)
    genre_song_count = df.groupby('genre')['song_title'].count()
    st.subheader("Number of Songs per Genre")

    fig2 = px.bar(
            genre_song_count,
            x=genre_song_count.index,
            y=genre_song_count.values,
            title="Number of Songs per Genre",
            color='song_title'
        )

    st.plotly_chart(fig2, use_container_width=True)


if select == "Streaming Status":
    st.title("Streaming Status Analysis")

    total_streams = df["stream"].sum()
    avg_streams = round(df["stream"].mean(), 2)
    max_streams = df["stream"].max()
    min_streams = df["stream"].min()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Streams", f"{total_streams:,}")
    col2.metric("Average Streams", f"{avg_streams:,.2f}")
    col3.metric("Max Streams", f"{max_streams:,}")
    col4.metric("Min Streams", f"{min_streams:,}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top 10 Most Streamed Songs")
        top_streamed_songs = df.nlargest(10, "stream")
        fig_songs = px.bar(
            top_streamed_songs,
            x="stream",
            y="song_title",
            orientation='h',
            color="artist",
            title="Top 10 Songs by Streams"
        )
        st.plotly_chart(fig_songs, use_container_width=True)

    with col_right:
        st.subheader("Top 10 Most Streamed Artists")
        artist_streams = df.groupby("artist")["stream"].sum().reset_index().nlargest(10, "stream")
        fig_artists = px.pie(
            artist_streams,
            values="stream",
            names="artist",
            title="Artist Share by Streams"
        )
        st.plotly_chart(fig_artists, use_container_width=True)

    st.divider()

    st.subheader("Relationship between Popularity and Streams")
    fig_scatter = px.scatter(
        df,
        x="popularity",
        y="stream",
        color="genre",
        hover_data=["song_title", "artist"],
        title="Popularity vs. Streams Correlation"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Streams by Explicit Content")
    explicit_streams = df.groupby("explicit_content")["stream"].mean().reset_index()
    fig_explicit = px.bar(
        explicit_streams,
        x="explicit_content",
        y="stream",
        color="explicit_content",
        title="Average Streams: Explicit vs. Non-Explicit"
    )
    st.plotly_chart(fig_explicit, use_container_width=True)

if select == "Dataset View":
    st.title("📂 Spotify Dataset Explorer")
    st.write("Browse, filter, and analyze the raw Spotify dataset.")
    st.divider()

    # Top Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records", f"{df.shape[0]:,}")
    m2.metric("Total Columns", df.shape[1])
    m3.metric("Missing Cells", df.isna().sum().sum())
    m4.metric("Memory Usage", f"{df.memory_usage().sum() / 1024:.1f} KB")

    st.divider()

    # Create Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Data Explorer", "📈 Column Statistics", "📥 Export Data"])

    with tab1:
        st.subheader("Data Filters & Search")

        # Filtering Row
        f_col1, f_col2, f_col3 = st.columns([2, 2, 3])

        with f_col1:
            # Select column to filter
            filter_col = st.selectbox("Filter by Column", ["None"] + list(df.columns))

        with f_col2:
            # Select value based on column
            if filter_col != "None":
                unique_vals = sorted(df[filter_col].dropna().unique().astype(str))
                selected_val = st.selectbox(f"Select {filter_col}", unique_vals)
            else:
                st.write("Select a column to filter")

        with f_col3:
            # Global Search
            search_query = st.text_input("Global Search (Title, Artist, etc.)", placeholder="Search anything...")

        # Apply Filters
        filtered_df = df.copy()

        if filter_col != "None":
            filtered_df = filtered_df[filtered_df[filter_col].astype(str) == selected_val]

        if search_query:
            # Case-insensitive global search across all columns
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]

        # Column Selection
        st.subheader("Display Settings")
        all_cols = list(df.columns)
        display_cols = st.multiselect("Columns to show", all_cols, default=all_cols[:8])

        # Row selection slider
        num_rows = st.slider("Number of rows to display", 5, len(filtered_df), min(50, len(filtered_df)))

        # Display the dataframe
        st.dataframe(filtered_df[display_cols].head(num_rows), use_container_width=True)
        st.info(f"Showing {min(num_rows, len(filtered_df))} of {len(filtered_df)} filtered records.")

    with tab2:
        st.subheader("Dataset Summary Statistics")

        # Numerical stats
        st.write("**Numerical Columns Summary**")
        st.dataframe(df.describe().T, use_container_width=True)

        # Column types and Nulls
        st.divider()
        st.write("**Data Types & Null Counts**")
        type_info = pd.DataFrame({
            'Data Type': df.dtypes.astype(str),
            'Non-Null Count': df.notnull().sum(),
            'Null Count': df.isnull().sum(),
            'Null %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        st.dataframe(type_info, use_container_width=True)

    with tab3:
        st.subheader("Download Filtered Dataset")
        st.write("Export your current filtered view as a CSV file.")

        # Prepare CSV for download
        csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="spotify_filtered_data.csv",
            mime="text/csv",
            help="Click to download the currently filtered dataset."
        )

        st.write("**Preview for Export:**")
        st.write(f"Columns: {', '.join(display_cols)}")
        st.write(f"Total rows to be exported: {len(filtered_df)}")


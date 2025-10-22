import requests
import json
import time
import pandas as pd

tags_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/tags.csv")
links_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/links.csv")
ratings_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/ratings.csv")
movies_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/movies.csv")
genome_tags_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/genome-tags.csv")
genome_scores_df= pd.read_csv("C:/Users/Daksh/Desktop/movie-recommendation/data/development/ml-latest/genome-scores.csv")

# Step 1: Compute average ratings
avg_ratings = ratings_df.groupby('movieId')['rating'].mean().reset_index(name='avg_rating')

# Step 2: Aggregate user tags
tags_df['tag'] = tags_df['tag'].astype(str)
user_tags = tags_df.groupby('movieId')['tag'].apply(lambda x: '|'.join(x.unique())).reset_index(name='user_tags')

# Step 3: Genome relevances
genome_merged = genome_scores_df.merge(genome_tags_df, on='tagId')
genome_dicts = genome_merged.groupby('movieId').apply(
    lambda x: json.dumps(dict(zip(x['tag'], x['relevance'])))
).reset_index(name='genome_relevances')

# Step 4: Merge base data
enriched_df = movies_df.merge(links_df, on='movieId', how='left')
enriched_df = enriched_df.merge(avg_ratings, on='movieId', how='left')
enriched_df = enriched_df.merge(user_tags, on='movieId', how='left')
enriched_df = enriched_df.merge(genome_dicts, on='movieId', how='left')

# Fill NaNs
enriched_df['avg_rating'] = enriched_df['avg_rating'].fillna(0)
enriched_df['user_tags'] = enriched_df['user_tags'].fillna('')
enriched_df['genome_relevances'] = enriched_df['genome_relevances'].fillna('{}')

# Step 5: TMDB fetch setup
TMDB_API_KEY = '549d74d021bd35eac9d680ec3ec9aacf'  # replace with your key
BASE_URL = 'https://api.themoviedb.org/3/movie/'
IMAGE_BASE = 'https://image.tmdb.org/t/p/w500/'

def fetch_tmdb_details(tmdb_id):
    if pd.isna(tmdb_id):
        return None, None, None, None
    url = f"{BASE_URL}{int(tmdb_id)}?api_key={TMDB_API_KEY}&append_to_response=credits"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            overview = data.get('overview', '')
            poster_path = data.get('poster_path', '')
            poster_url = f"{IMAGE_BASE}{poster_path}" if poster_path else ''

            directors = [crew['name'] for crew in data['credits']['crew'] if crew['job'] == 'Director']
            director = '|'.join(directors[:3])

            actors = [cast['name'] for cast in data['credits']['cast'][:5]]
            actors_str = '|'.join(actors)

            return director, actors_str, overview, poster_url
        else:
            return None, None, None, None
    except Exception:
        return None, None, None, None

# Step 6: Initialize columns
enriched_df['director'] = ''
enriched_df['actors'] = ''
enriched_df['overview'] = ''
enriched_df['poster_url'] = ''

# ⚡ Limit to first 1000 records
subset_df = enriched_df.head(1000).copy()

# Fetch TMDB data
for idx, row in subset_df.iterrows():
    print(f"Fetching TMDB data for {row['title']} ({idx+1} of {len(subset_df)})")
    director, actors, overview, poster_url = fetch_tmdb_details(row['tmdbId'])
    subset_df.at[idx, 'director'] = director or ''
    subset_df.at[idx, 'actors'] = actors or ''
    subset_df.at[idx, 'overview'] = overview or ''
    subset_df.at[idx, 'poster_url'] = poster_url or ''

    if idx % 40 == 0 and idx > 0:
        time.sleep(1)  # prevent rate limit issues

# Save the subset to CSV
subset_df.to_csv('enriched_movies_1000.csv', index=False)
print("✅ Enriched CSV created: enriched_movies_1000.csv (first 1000 records)")


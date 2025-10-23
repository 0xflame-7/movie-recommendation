# Task 1: Script for Dataset Creation via TMDB

I'll start with Task 1, as it's foundational for enriching the dataset. Since the MovieLens dataset provides tmdbId in links.csv, we can use the TMDB API to fetch additional details like actors, directors, poster paths, overviews, titles (fresh from TMDB to ensure accuracy), and original language. We'll keep genres from the MovieLens movies.csv (as specified), and merge in other fields from the dataset (e.g., movieId, imdbId).

For computations:

- avg_rating: Average of all ratings for that movie from ratings.csv.
- total_rating_users: Count of unique users who rated the movie (not total ratings, as some users might rate multiple times, but in this dataset, it's one rating per user-movie pair).
- popularity_score: I'll compute a simple score as (avg_rating \* log(total_rating_users + 1)) to weigh highly rated movies with more ratings higher. This is a common heuristic; adjust if needed.

## Important Notes

- This script assumes you have the full MovieLens dataset files (links.csv, movies.csv, ratings.csv) in the same directory. The snippets you provided are incomplete, so you'll need to download the full ml-latest-small.zip from <https://grouplens.org/datasets/movielens/latest/>.
- You need a free TMDB API key: Sign up at <https://www.themoviedb.org/>, get your key, and replace 'YOUR_TMDB_API_KEY' in the script.
- The script uses Python with pandas for data handling and requests for API calls. Install them via pip install pandas requests if needed.
- TMDB API has rate limits (~40 requests/second), so I've added a sleep to avoid bans. For 9742 movies, it might take ~30-60 minutes.

## Output

- A new enriched_movies.csv with all fields merged.

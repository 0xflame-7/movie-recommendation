import pandas as pd
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import asyncio
import logging
import os
import asyncio

# Setup logging for errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.db import engine, init_db  # AsyncEngine from your db setup
from src.api.models import Genre, Actor, Director, Movie  # Import schemas


genre_image_urls = {
    "Action": "https://decider.com/wp-content/uploads/2024/04/ACTION-PEACOCK-REVIEW.jpg?quality=75&strip=all&w=1200",
    "Adventure": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCsgOcVcuvUFMRUB5ncjeC34YNOuCv6CPRrg&s",
    "Animation": "https://submarine.nl/app/uploads/2019/09/Undon_Tease-Art_1920x1080-2.jpg",
    "Children": "https://media.timeout.com/images/105501822/750/562/image.jpg",
    "Comedy": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRiHZU364SMmhPY2PmvBTC7gABB14M4Zbl5RA&s",
    "Crime": "https://m.media-amazon.com/images/M/MV5BOWJlZjgxZTgtOTlhYy00ZjI4LWI3ZDQtYzI2MjM3OTFiMzk3XkEyXkFqcGc@._V1_.jpg",
    "Documentary": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSUc4Bs4e3eue1INoXOpRYFw08g-We7tJiRFE3uzb41Y8hKLSEjHpl6g5asrH8R7383y8&usqp=CAU",
    "Drama": "https://static01.nyt.com/images/2023/02/03/multimedia/02endgame1-lzpc/02endgame1-lzpc-superJumbo.jpg",
    "Fantasy": "https://images.filmibeat.com/webp/img/popcorn/movie_lists/7-epic-hollywood-fantasy-movies-that-will-take-you-beyond-reality-20241217113256-1561.jpg",
    "Film-Noir": "https://d150u0abw3r906.cloudfront.net/wp-content/uploads/2022/02/New-Project-4-1.jpg",
    "Horror": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQF6QTrCn8dyV5EfY91eH-bAikiWIkW8Kba2Q&s",
    "Musical": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_FqzeOYCC3Bwk2-RGGOW2WZnqo_l1vhw1kQ&s",
    "Mystery": "https://m.media-amazon.com/images/M/MV5BMWRmZjEzMjYtZjUzYS00NzRiLWI0NWUtMTNjYjhkZWQ1OTFjXkEyXkFqcGc@._V1_.jpg",
    "Romance": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjQ-VdNcM8CZXrgAiz4r-ThpALvX9TlvdGPA&s",
    "Sci-Fi": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbNcakROKpaiYiPlUQq9qDc3CEDX_H11GAEg&s",
    "Western": "https://lionsgate.brightspotcdn.com/e5/84/a7452b98408f89441cb6518b9684/the-old-way-movies-he-bg-mbl-01.jpg",
    "War": "https://www.usni.org/sites/default/files/styles/hero_image_1600/public/Cobb-PRO-9-24-1%20Hero.jpg?itok=_WjzQAUY",
    "Thriller": "https://assets.gqindia.com/photos/67c0b25c29cbda9fdc7376ee/16:9/w_2560%2Cc_limit/daily-BW-for-March-17-Crime-thrillers-based-on-true-stories.jpg",
}


async def seed_db():
    await init_db()
    logger.info("Database tables created.")

    # Create async session factory
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        # Load CSV data
        print(os.listdir())
        df = pd.read_csv("src/model/data/clean_data.csv")
        logger.info(f"Loaded {len(df)} rows from CSV.")
    except FileNotFoundError:
        logger.error("CSV file not found at model/data/clean_data.csv. Check path.")
        return
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return

    async with async_session() as session:
        try:
            # Genres: Unique from pipe-separated
            all_genres = set()
            for genres_str in df["genres"].unique():
                if pd.notna(genres_str):
                    all_genres.update(genres_str.split("|"))
            logger.info(f"Found {len(all_genres)} unique genres.")
            for name in all_genres:
                result = await session.execute(select(Genre).where(Genre.name == name))
                existing_genre = result.scalars().first()
                if not existing_genre:
                    session.add(Genre(name=name, image_url=genre_image_urls.get(name)))

            await session.commit()
            logger.info("Seeded genres.")

            df_actors = pd.read_csv(
                "src/model/data/actor_summary.csv", usecols=["actor", "image_url"]
            )
            logger.info(f"Loaded {len(df_actors)} actors from actor_summary.csv")
            # Actors: Unique from pipe-separated
            count = 0
            for _, row in df_actors.iterrows():
                name, img = row["actor"], row["image_url"]
                result = await session.execute(select(Actor).where(Actor.name == name))
                if not result.scalars().first():
                    session.add(Actor(name=name, image_url=img))
                    count += 1
                    if count % 50 == 0:
                        await session.commit()
                        logger.info(f"Committed {count} actors...")
            await session.commit()
            logger.info("Seeded actors.")

            df_director = pd.read_csv(
                "src/model/data/director_summary.csv", usecols=["director", "image_url"]
            )
            logger.info(
                f"Loaded {len(df_director)} directors from director_summary.csv"
            )
            # Directors: Unique from pipe-separated
            count = 0
            for _, row in df_director.iterrows():
                name, img = row["director"], row["image_url"]
                result = await session.execute(
                    select(Director).where(Director.name == name)
                )
                if not result.scalars().first():
                    session.add(Director(name=name, image_url=img))
                    count += 1
                    if count % 50 == 0:
                        await session.commit()
                        logger.info(f"Committed {count} directors...")
            await session.commit()
            logger.info("Seeded directors.")

            # Movies: Insert all, with type casting where needed
            inserted_count = 0
            for _, row in df.iterrows():
                result = await session.execute(
                    select(Movie).where(Movie.id == (row["movieId"]))
                )
                if not result.scalars().first():
                    session.add(
                        Movie(
                            id=int(row["movieId"]),
                            original_title=row["original_title"],
                            genres=row["genres"],
                            actors=row["actors"],
                            directors=row["directors"],
                            overview=row["overview"],
                            original_language=row["original_language"],
                            poster_path=row["poster_path"],
                            avg_rating=float(row["avg_rating"]),
                            total_rating_users=(
                                int(row["total_rating_users"])
                                if pd.notna(row["total_rating_users"])
                                else 0
                            ),
                            popularity_score=(
                                float(row["popularity_score"])
                                if pd.notna(row["popularity_score"])
                                else 0.0
                            ),
                            tmdbId=int(row["tmdbId"]),
                            decade=row["decade"],
                        )
                    )
                    inserted_count += 1

                    if inserted_count % 100 == 0:
                        await session.commit()
                        logger.info(f"Inserted {inserted_count} movies...")
            await session.commit()
            logger.info(f"Seeded {inserted_count} movies.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Database error during seeding: {e}")
            raise


# Run the seeding function (for testing or manual execution)
if __name__ == "__main__":
    asyncio.run(seed_db())

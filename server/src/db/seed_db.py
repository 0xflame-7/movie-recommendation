import pandas as pd
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import asyncio
import logging
import os

# Setup logging for errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.db import engine, init_db  # AsyncEngine from your db setup
from src.api.models import Genre, Actor, Director, Movie  # Import schemas


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
                    session.add(Genre(name=name))
            await session.commit()
            logger.info("Seeded genres.")

            # Actors: Unique from pipe-separated
            all_actors = set()
            for actors_str in df["actors"].dropna():
                all_actors.update(actors_str.split("|"))
            logger.info(f"Found {len(all_actors)} unique actors.")
            for name in all_actors:
                result = await session.execute(select(Actor).where(Actor.name == name))
                existing_actor = result.scalars().first()
                if not existing_actor:
                    session.add(Actor(name=name))
            await session.commit()
            logger.info("Seeded actors.")

            # Directors: Unique from pipe-separated
            all_directors = set()
            for directors_str in df["directors"].dropna():
                all_directors.update(directors_str.split("|"))
            logger.info(f"Found {len(all_directors)} unique directors.")
            for name in all_directors:
                result = await session.execute(
                    select(Director).where(Director.name == name)
                )
                existing_director = result.scalars().first()
                if not existing_director:
                    session.add(Director(name=name))
            await session.commit()
            logger.info("Seeded directors.")

            # Movies: Insert all, with type casting where needed
            inserted_count = 0
            for _, row in df.iterrows():
                result = await session.execute(
                    select(Movie).where(Movie.id == row["movieId"])
                )
                existing_movie = result.scalars().first()
                if not existing_movie:
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
                            avg_rating=(float(row["avg_rating"])),
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
                            decade=(row["decade"]),
                        )
                    )
                    inserted_count += 1
            await session.commit()
            logger.info(f"Seeded {inserted_count} movies.")

        except Exception as e:
            await session.rollback()
            logger.error(f"Database error during seeding: {e}")
            raise


# Run the seeding function (for testing or manual execution)
if __name__ == "__main__":
    asyncio.run(seed_db())

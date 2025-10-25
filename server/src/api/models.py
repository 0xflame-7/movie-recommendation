from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List


class User(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    profilePic: str | None = Field(default=None)
    email_verified: bool | None = Field(default=False, nullable=False)
    is_active: bool | None = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"


class UserAuth(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    provider: AuthProvider | None = Field(default=AuthProvider.EMAIL, nullable=False)

    email: str = Field(nullable=False, index=True, unique=True)
    password: str | None = Field(default=None, nullable=True, repr=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Session(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    user_agent: str | None = Field(default=None, nullable=True)
    ip_address: str | None = Field(default=None, nullable=True)
    refresh_token: str = Field(default=None, nullable=True, repr=False)
    valid: bool | None = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Genre(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    image_url: str | None = Field(default=None, nullable=True)


class Actor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    image_url: str | None = Field(default=None, nullable=True)


class Director(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    image_url: str | None = Field(default=None, nullable=True)


class Movie(SQLModel, table=True):
    id: int = Field(primary_key=True)
    original_title: str = Field(index=True)
    genres: str
    actors: str
    directors: str
    overview: str
    original_language: str
    poster_path: str
    avg_rating: float
    total_rating_users: int
    popularity_score: float
    tmdbId: int
    decade: str


class UserPreference(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    linked_genres: List["UserGenreLink"] = Relationship(
        back_populates="user_preference"
    )
    linked_actors: List["UserActorLink"] = Relationship(
        back_populates="user_preference"
    )
    linked_directors: List["UserDirectorLink"] = Relationship(
        back_populates="user_preference"
    )
    linked_movies: List["UserMovieLink"] = Relationship(
        back_populates="user_preference"
    )


class UserGenreLink(SQLModel, table=True):
    user_preference_id: uuid.UUID = Field(
        foreign_key="userpreference.id", primary_key=True
    )
    genre_id: uuid.UUID = Field(foreign_key="genre.id", primary_key=True)
    user_preference: UserPreference = Relationship(back_populates="linked_genres")


class UserActorLink(SQLModel, table=True):
    user_preference_id: uuid.UUID = Field(
        foreign_key="userpreference.id", primary_key=True
    )
    actor_id: uuid.UUID = Field(foreign_key="actor.id", primary_key=True)
    user_preference: UserPreference = Relationship(back_populates="linked_actors")


class UserDirectorLink(SQLModel, table=True):
    user_preference_id: uuid.UUID = Field(
        foreign_key="userpreference.id", primary_key=True
    )
    director_id: uuid.UUID = Field(foreign_key="director.id", primary_key=True)
    user_preference: UserPreference = Relationship(back_populates="linked_directors")


class UserMovieLink(SQLModel, table=True):
    user_preference_id: uuid.UUID = Field(
        foreign_key="userpreference.id", primary_key=True
    )
    movie_id: int = Field(foreign_key="movie.id", primary_key=True)
    user_preference: UserPreference = Relationship(back_populates="linked_movies")


# Ratings table (for real and pseudo-ratings)
class UserRating(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    movie_id: int = Field(foreign_key="movie.id", primary_key=True)
    rating: float = Field(ge=0.5, le=5.0)  # 0.5 increments
    is_pseudo: bool = Field(default=True)  # Flag for pseudo vs real
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

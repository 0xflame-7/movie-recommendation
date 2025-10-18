run:
	cd server && uv run uvicorn src:app --host 0.0.0.0 --port 8000 --reload

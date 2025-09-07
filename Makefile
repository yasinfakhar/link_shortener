watch:
	python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8005 --reload

prod:
	python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8005
install:
	pip install -r requirements.txt
	pip install pytest ruff

test:
	pytest tests/ -v

lint:
	ruff check src/ --exit-zero

run:
	python3 main.py

ui:
	python3 -m streamlit run src/ui/dashboard.py

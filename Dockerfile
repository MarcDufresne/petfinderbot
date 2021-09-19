FROM python:3.8

WORKDIR /app

ADD petfinderbot/__init__.py petfinderbot/__init__.py
ADD pyproject.toml .
ADD poetry.lock .

RUN pip install --no-cache-dir poetry==1.1.4 \
    && poetry config virtualenvs.in-project true \
    && poetry install --no-dev \
    && poetry cache clear -n --all pypi

ADD petfinderbot petfinderbot
ADD run.py .

CMD ["poetry", "run", "python", "run.py"]

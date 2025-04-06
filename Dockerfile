FROM python:3.11.6

WORKDIR /app
# prepara entorno de python
ENV PYTHONPATH=${PYTHONPATH}:/app


RUN apt-get update && apt-get install -y curl

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"


# RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# enable execute file
RUN chmod +x entrypoint.sh

# by default use python
ENV APP_MODE=python

EXPOSE 8080
EXPOSE 5676

# Definir el entrypoint
ENTRYPOINT ["./entrypoint.sh"]


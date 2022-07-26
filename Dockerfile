FROM python:3.9 as python
WORKDIR /app

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vvv

FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app
CMD todoistbot/todoistBot.py --config=$TODOIST_CONFIG_PATH
#
#
# Build container
FROM python:3 AS build-python

RUN useradd -m www
USER www:www
ENV PATH=/srv/.local/bin:$PATH

COPY --chown=www:www Pipfile Pipfile.lock /srv/www/

WORKDIR /srv/www
RUN export PATH=$HOME/.local/bin:$PATH \
    && pip install --user --no-cache-dir pipenv \
    && PIPENV_VENV_IN_PROJECT=true pipenv install

COPY --chown=www:www api/ /srv/www/api/

#
#
# Release container
FROM python:3-slim as release

RUN useradd -m www
USER www:www

ENV PATH=/srv/www/.venv/bin:$PATH

COPY --from=build-python --chown=www:www /srv/www /srv/www

WORKDIR /srv/www
ENTRYPOINT ["python", "api/api.py", "--port=8001"]

#
#
# Test container
FROM release as test

RUN pip install --no-cache-dir pipenv \
    && PIPENV_VENV_IN_PROJECT=true pipenv install --dev

COPY --chown=www:www tests/ /srv/www/tests/

ENTRYPOINT ["nosetests", "-s"]

#
#
# Make sure if no --target is specified, the release container is built
FROM release

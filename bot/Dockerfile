FROM python:3.14-alpine AS build
ENV PYTHONUNBUFFERED=1
ENV DOCKER=1

RUN apk --no-cache add alpine-sdk
RUN pip install --no-cache-dir pipenv
COPY ./Pipfile Pipfile.lock /build/
WORKDIR /build/
RUN pipenv install --system --deploy

COPY librarian /app/librarian

FROM python:3.14-alpine AS runner

ENV CONFIG_DIR=/config/
RUN apk --no-cache add git
RUN mkdir /config

COPY --from=build /app /app
COPY --from=build /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/


WORKDIR /app
ENTRYPOINT ["python", "-m", "librarian.main",  "/config"]
LABEL org.opencontainers.image.source=https://github.com/tech-6/librarian \
    org.opencontainers.image.description="Funny Crimes Bot" \
    org.opencontainers.image.licenses="All Rights Reserved"
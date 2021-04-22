FROM python:3.8-alpine
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="Shit&Sticks CI" \
      org.label-schema.url="https://github.com/mike0sv/ssci" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/mike0sv/ssci" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"
LABEL maintainer="mike0sv@gmail.com"


RUN apk add --no-cache git docker-compose docker

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .

CMD python -u ssci.py
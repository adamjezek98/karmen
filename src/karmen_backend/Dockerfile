FROM python:3.7-slim

WORKDIR /usr/src/app

# common requirements (with fakeprinter)
RUN set -e && apt-get update && apt-get install --yes git gcc make postgresql-client libffi-dev jq libpq-dev libpcre2-8-0 python3-dev bash build-essential
RUN set -e && pip install --upgrade pip pipenv
 # linux-headers-$(uname -r) \

# specific for backend
#RUN set -e && apt-get install --yes libxml2-dev libxslt-dev nginx gettext avahi-utils arp-scan dbus
#RUN set -e && pip install uwsgi supervisor

# set permition for upload directory (to mount later)
##RUN mkdir /tmp/karmen-files \
#    && chown www-data:www-data /tmp/karmen-files \
#    && chmod -R g+sw /tmp/karmen-files

# Install from lockfile
COPY Pipfile* ./
RUN set -e && pipenv lock -r > requirements.pip && pip install -r requirements.pip
# remove build requirements not required anymore
RUN apt-get remove --purge --yes gcc make postgresql-client libpq-dev libffi-dev python3-dev

# runtime deps
ENV PYTHONPATH=$PYTHONPATH:/usr/src/app

COPY . .

CMD ./scripts/docker-start.sh



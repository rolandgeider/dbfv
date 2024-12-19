# Note: you MUST build this image from the project's root!
# docker build -f docker/Dockerfile --tag dbfv/server .
#

#FROM httpd:2.4-bookworm
FROM ubuntu:24.04
LABEL maintainer="Roland Geider <roland@geider.net>"
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm
ARG DOCKER_DIR=./docker

RUN apt update \
  && apt install --no-install-recommends -y \
      adduser \
      locales \
      python3-pip \
      python3-venv \
      python3-wheel \
      sqlite3 \
      wget \
      tzdata \
      apache2 \
      libapache2-mod-wsgi-py3 \
  && locale-gen en_US.UTF-8 \
  && rm -rf /var/lib/apt/lists/* \
  && adduser dbfv  --disabled-password --gecos ""


COPY --chown=dbfv:www-data ./requirements.txt /home/dbfv/src/requirements.txt
COPY ${DOCKER_DIR}/dbfv.conf /etc/apache2/sites-available/
COPY --chown=dbfv:dbfv ${DOCKER_DIR}/dbfv.conf /etc/apache2/sites-available/
RUN a2dissite 000-default.conf \
  && a2enmod headers \
  && a2ensite dbfv \
  && echo "ServerName localhost" >> /etc/apache2/conf-available/fqdn.conf \
  && a2enconf fqdn \
  && usermod -G dbfv www-data

RUN ln -s /home/dbfv/static/CACHE /var/www
USER dbfv

WORKDIR /home/dbfv/src
RUN python3 -m venv /home/dbfv/venv

# Change permissions of some files and folders so the apache process
# can access them.
#RUN mkdir -p ~/static/CACHE ~/media \
#  && ln -s /home/dbfv/static/CACHE /home/dbfv/src/CACHE \
#  && chmod g+w /home/dbfv/static/CACHE

RUN . /home/dbfv/venv/bin/activate \
  && pip install --upgrade pip \
  && pip install --no-cache -r requirements.txt

COPY --chown=dbfv:www-data . /home/dbfv/src
RUN . /home/dbfv/venv/bin/activate  \
    && python3 manage.py collectstatic --no-input

USER root
RUN  chown dbfv:www-data -R /home/dbfv/static
#     && chmod -R g+x /home/dbfv/src

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
# Use the latest Python 3 docker image
FROM bids/freesurfer:v6.0.1-5

MAINTAINER Flywheel <support@flywheel.io>

RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -

RUN apt-get update && \
    apt-get install -y \
    nodejs \
    zip && \
    rm -rf /var/lib/apt/lists/* 
# The last line above is to help keep the docker image smaller

RUN npm install -g bids-validator@1.3.12

RUN apt-get  update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:jonathonf/python-3.6

# Tried this one too
#    add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update && \
    apt-get install -y python3.6 && \
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python3.6

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.6 get-pip.py && \
    pip3.6 install --upgrade pip 

RUN apt-get update

RUN pip3.6 install virtualenv 

ENV VIRTUAL_ENV=/opt/venv
RUN python3.6 -m virtualenv --python=/usr/bin/python3.6 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip3.6 install flywheel-sdk==10.4.1 \
        flywheel-bids==0.8.2 && \
    rm -rf /root/.cache/pip

#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Save docker environ
ENV PYTHONUNBUFFERED 1
RUN python -c 'import os, json; f = open("/tmp/gear_environ.json", "w"); json.dump(dict(os.environ), f)' 

# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["/flywheel/v0/run.py"]

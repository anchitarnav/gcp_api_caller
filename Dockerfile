FROM ubuntu:18.04

# Updating apt
RUN apt-get -y update

# Install Google SDK
## pre-preparations
RUN echo 'deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main' | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN apt-get -y install apt-transport-https ca-certificates gnupg
RUN apt-get -y install curl
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

## install GCP sdk


# update again to ensure that the new source is considered
RUN apt-get -y update
RUN apt-get install -y google-cloud-sdk

## validation
RUN gcloud --version

## Installing python
RUN apt-get install -y python3-pip

RUN ln $(which python3) /bin/python
RUN ln $(which pip3) /bin/pip

ADD . /root
WORKDIR /root
RUN pip install -r requirements.txt

CMD ["python3", "app.py"]

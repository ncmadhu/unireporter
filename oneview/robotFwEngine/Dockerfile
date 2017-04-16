# set the base image to ubuntu
FROM ubuntu:latest

# File Author
MAINTAINER Madhu Chakravarthy

# Update the sources list
RUN apt-get update

# Install Python and Basic Python Tools
RUN apt-get install -y build-essential libssl-dev libffi-dev
RUN apt-get install -y python python-dev python-distribute python-pip vim
RUN pip install --upgrade pip

# Copy the code
ADD ./config/ /usr/src/oneview/config
ADD ./lib/ /usr/src/oneview/lib
ADD ./log/ /usr/src/oneview/log
ADD ./reports/ /usr/src/oneview/reports

# Set the default directory where CMD will execute
WORKDIR /usr/src/oneview/lib

# Install python requirements
RUN pip install -r requirements.txt

# Set the default command to execute    
# when creating a new container
#CMD python main.py

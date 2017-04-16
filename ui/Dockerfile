# Set the base image to node 
FROM node:7.8.0 

# File Author / Maintainer
MAINTAINER Madhu Chakravarthy

#copy the node application 
ADD . /usr/src/oneview/

# Set the default directory where CMD will execute
WORKDIR /usr/src/oneview

# Install node modules
RUN npm install


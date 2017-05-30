# UNIREPORTER

PoC application to manage several test frameworks using a single UI pane. 
UI is used to view the test reports and trigger the tests in the connected test machines using ssh


# Docker
Used docker to tie up all the below components
1. RabbitMQ
   1. Used for messaging between node.js and the corresponding test framework container
2. MongoDB
   1. Used for storing the tests results and querying the results from UI and test framework container
3. node.js - 
   1. Backend server for serving UI requests
   2. Backend server for sending message to RabbitMQ according the UI requests
   3. Backend server for to query result data from mongoDB according to UI requests
4. Test framework container
      1. Develop a container specific for your test framework to do below tasks
            1. Start the test when receiving start message from RabbitMQ sent by UI
            2. Copy the reports from test executor
            3. Parse the test reports
            4. update the mongoDB with the parsed test reports
      2. In my example I have used Robot Framework and developed a container for it.
      3. Add your framework specific urls and messaging code in node.js
      4. Write a Docker file for your test framework
      4. Add your framework container details in docker-compose.yml
5. Start your containers in one step using docker-compose up

# To install docker

https://docs.docker.com/engine/installation/linux/ubuntu/#os-requirements

# To install docker-compose use below link

https://docs.docker.com/compose/install/

Docker compose needs docker api version greater than 1.10.0

# Passwordless ssh access Example setup
ssh-keygen -t rsa

ssh ansible@192.168.56.101 mkdir -p .ssh

cat ~/.ssh/ansible_rsa.pub | ssh ansible@192.168.56.101 'cat >> .ssh/authorized_keys'

ssh ansible@192.168.56.101 "chmod 700 .ssh; chmod 640 .ssh/authorized_keys"

ssh ansible@192.168.56.101

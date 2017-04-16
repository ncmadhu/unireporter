# UNIREPORTER

PoC application to manage several test frameworks using a single UI pane. 
UI is used to view the test reports and trigger the tests in the connected test machines using ssh

# Docker
Used to docker to tie up all the below components
1. RabbitMQ - Used for messaging between UI and the corresponding framework container
2. MongoDB - Used for storing the tests results
3. node.js - Backend server for sending message to RabbitMQ
4. Test framework container -  Develop a container specific for your test framework to start the test, parse the test reports
   and add the results to mongodb. Add your test framework container specific rabbitmq message format apis in node.js and URLS
   Add your contaner image in docker-compose.yml. In my example I have used robot framework in my example code.
5. Start your containers in step using docker-compose up

# Serverless Function, Monitoring Dashboard and Custom Runtime

In this project there are 3 major implementations:
i) a serverless function to fetch traffic and analyze resource usage metrics from the server;
ii) a dashboard that allows users to see all data monitored and analyzed by the serverless funciton;
iii) a custom serverless runtime that allows this and other functions to run on the server

## Monitoring Function

It was developed a servereless function to process the periodic resource use measurements.

The system collects resource usage information using the psutil module. Measurements are stored in a key named metrics under Redis.

The function computes two stateless metrics: the percentage of outgoing traffic bytes and the percentage of memory caching content. And also, computes the moving average utilization of each CPU over the last minute.

## Monitoring Dashboard

A Kubernetes pod was built to display the monitoring information computed by the serverless function. 

It was used the Plotly framework to help and the improve the development. 

The data was collected from the Redis, processed by the script and showed in the dashboard, in a easily and friendly way. 

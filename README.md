# RRDReST
simple micro service for converting your RRD's to web services

![rrdReST](/rrdshot.PNG)

### getting started
- ensure you have ```rrdtool``` installed and you can access the rrd files from the server
- git clone the project ``` git clone https://github.com/tbotnz/RRDReST && cd RRDReST ```
- install the requirements ```pip3 install -r requirements.txt```
- run the app with uvicorn ```uvicorn rrdrest:rrd_rest --host "0.0.0.0" --port 9000```

### rrdtool
- tested with version 1.7
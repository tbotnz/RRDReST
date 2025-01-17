# RRDReST
simple micro service for converting your RRD's to web services

![rrdReST](/rrdshot.PNG)

### getting started
- ensure you have ```rrdtool``` installed and you can access the rrd files from the server
- git clone the project ``` git clone https://github.com/tbotnz/RRDReST && cd RRDReST ```
- install the requirements ```pip3 install -r requirements.txt```
- run the app with uvicorn ```uvicorn rrdrest:rrd_rest --host "0.0.0.0" --port 9000```
- access the swagger documentation via ```http://127.0.0.1:9000/docs```

### examples
- last 24 hours ```curl 127.0.0.1:9000/?rrd_path=tests/port-id15.rrd```
- epoch date time filter ```curl 127.0.0.1:9000/?rrd_path=tests/port-id15.rrd&epoch_start_time=1622109000&epoch_end_time=1624787400```
- time output in epoch ```curl 127.0.0.1:9000/?rrd_path=tests/port-id15.rrd&epoch_start_time=1622109000&epoch_end_time=1624787400&epoch_output=true```

### rrdtool
- tested with version 1.7

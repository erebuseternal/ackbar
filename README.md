# ackbar

## Docker Instructions

#### Building the Image
`docker build -t "mgietzmann/ackbar:latest" .`

#### Running the Image
`docker run -p 8888:8888 -p 8000:22 -d --name=admiral_ackbar mgietzmann/ackbar:latest`

#### SSH into the Container
`ssh root@localhost -p 8000`

#### Stopping the Container
`docker container stop admiral_ackbar`

#### Removing the Container
`docker container rm admiral_ackbar`

## Jupyter Instructions

#### Running Jupyter Lab
```
ssh root@localhost -p 8000
jupyter lab --ip=0.0.0.0 --allow-root
exit
```

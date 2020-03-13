# ackbar

## Docker Instructions

#### Building the Image
`docker build -t "mgietzmann/datastore:latest" .`

#### Running the Image
`docker run -p 8889:8888 -p 8001:22 -d --name=datastore_server mgietzmann/datastore:latest`

#### SSH into the Container
`ssh root@localhost -p 8001`

## Jupyter Instructions

#### Running Jupyter Lab
```
ssh root@localhost -p 8001
jupyter lab --ip=0.0.0.0 --allow-root
exit
```
# ackbar

## Docker Instructions

#### Building the Image
`docker build -t "mgietzmann/webapp:latest" .`

#### Running the Image
`docker run -p 8889:8888 -p 8001:22 -p 5001:5001 -d --name=webapp mgietzmann/webapp:latest`

#### SSH into the Container
`ssh root@localhost -p 8000`

## Jupyter Instructions

#### Running Jupyter Lab
```
ssh root@localhost -p 8000
jupyter lab --ip=0.0.0.0 --allow-root
exit
```

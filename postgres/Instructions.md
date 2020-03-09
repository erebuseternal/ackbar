# ackbar

## Docker Instructions

#### Getting the Image
`docker pull postgres`

#### Running the Image
`docker run --name postgres_server -p 5432:5432 -e POSTGRES_PASSWORD=ackbar -d postgres`

#### Checking the Version
```
docker exec -it postgres_server bash
psql -U postgres
```

#### Using the Container
First you'll need to download the client side of Postgres to your local machine. Then you'll need to add the `bin/` folder to your Path variable. Once you've done both of those you'll be able to run:

`psql -U postgres`

Or use pgadmin4.


#### Finding the Docker Bridge Network Hostname
`docker network inspect bridge`
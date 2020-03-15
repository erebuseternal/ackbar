# ackbar

## Docker Instructions

#### Building the Image
`docker build -t "mgietzmann/datastore:latest" .`

#### Running the Image
`docker run -p 5000:5000 -d --name=datastore_server mgietzmann/datastore:latest`

## How to Push and Pull from Server

#### Example for Pushing
```python
import requests
BASE_URL = 'http://172.17.0.2:5000'
push_url = BASE_URL + '/push?bucket=test&key=pic.jpg'
files = {'upload': open('test/cat/5965ab07-23d2-11e8-a6a3-ec086b02610b.jpg','rb')}
requests.post(url, files=files)
```

#### Example for Pulling
```python
import requests
BASE_URL = 'http://172.17.0.2:5000'
pull_url = BASE_URL + '/pull?bucket=test&key=pic.jpg'
response = requests.get(pull_url)
with open('pic.jpg', 'wb') as fh:
    fh.write(response.content)
```
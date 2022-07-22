## Overview


## Requirements
Python 3.7+

## Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m aops_check
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t aops_check .

# starting up a container
docker run -p 8080:8080 aops_check
```
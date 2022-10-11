# Prototype implementation of High-threshold Asynchronous Distributed Key Generation

NOTE: This is a research implementation and may contain security issues. Do not use this for production.


# Running and benchmarking `adkg`
First, docker-compose will need to be installed if it has not been previously:

1. Install `Docker`_. (For Linux, see `Manage Docker as a non-root user`_) to
   run ``docker`` without ``sudo``.)

2. Install `docker-compose`.

Next, the image will need to be built  (this will likely take a while)
```
$ docker-compose build adkg
```

## Running tests and generating data points for adkg

You need to start a shell session in a container. The first run will take longer if the docker image hasn't already been built:
```
$ docker-compose run --rm adkg bash
```

Then, to test the `adkg` code locally, i.e., multiple thread in a single docker container, you need to run
```
$ pytest tests/test_adkg.py
```

### Debug using `vscode`
To debug the code using `vscode`, first uncomment the following from `Dockerfile`
```
# RUN pip install debugpy
# ENTRYPOINT [ "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m"]
```

Rebuild the `docker` images by runnning
```
docker-compose build adkg
```

Then `debug` by running the following command. Make sure to run the debugging in `vscode` after executing the following command. 
```
docker-compose run -p 5678:5678 adkg pytest tests/test_adkg.py 
```

### Run on multiple processes within a docker image
1. Start a docker image by running
```$docker-compose run --rm adkg bash ```

2. Start the ADKG instances
```$sh scripts/launch-tmuxlocal.sh apps/tutorial/adkg-tutorial.py conf/adkg/local```
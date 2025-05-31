# vulnerabilities
a web app for hacking  practice

## Running with Docker

To build and run this web application using Docker:

1.  **Build the Docker image:**
    Open your terminal in the project root directory (where the `Dockerfile` is located) and run:
    ```sh
    docker build -t lego-website .
    ```

2.  **Run the Docker container:**
    After the image is built successfully, run the following command to start a container. This will map port 2222 on your host machine to port 80 inside the container:
    ```sh
    docker run -d -p 2222:80 --name lego-website-container lego-website
    ```

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:2222`.

To stop and remove the container:
```sh
docker stop lego-website-container
docker rm lego-website-container
```

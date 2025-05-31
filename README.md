# vulnerabilities
a web app for hacking  practice

## Running with Docker

This application now uses a Flask backend with an SQLite database.

1.  **Build the Docker image:**
    Open your terminal in the project root directory (where the `Dockerfile` is located) and run:
    ```sh
    docker build -t lego-website .
    ```
    *(This command should remain the same unless you prefer a different image tag.)*

2.  **Run the Docker container:**
    After the image is built successfully, run the following command to start a container. This will map port 2222 on your host machine to port 5000 (where Flask is running) inside the container:
    ```sh
    docker run -d -p 2222:5000 --name lego-website-container lego-website
    ```
    When the container starts, it will automatically:
    *   Create an SQLite database file (`users.db`) within the container (in the `backend/instance` folder if you were to look inside the container).
    *   Create the necessary database tables.
    *   Create a default admin user with credentials: `admin` / `adminpassword`. (You should change the default admin password in a production environment).

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:2222 (or http://127.0.0.1:2222 if localhost does not work).`

4.  **Access the Admin Page:**
    To manage users, navigate to `http://localhost:2222/admin`.
    You may need to log in using the main application's login page with the admin credentials (`admin`/`adminpassword`) first to ensure any client-side flags for admin status are set, although the `/admin` route itself currently has simplified direct access for demonstration.

To stop and remove the container:
```sh
docker stop lego-website-container
docker rm lego-website-container
```

To view logs from the running container (useful for debugging or seeing Flask output):
```sh
docker logs -f lego-website-container
```

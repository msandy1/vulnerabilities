# vulnerabilities
ai created app nothing crazy speacial just target practice for cyber security study.

## Running with Docker

This application now uses a Flask backend with an SQLite database.

1.  **Build the Docker image:**
    Open your terminal in the project root directory (where the `Dockerfile` is located) and run:
    ```sh
    docker build -t lego-website .
    ```
    *(This command should remain the same unless you prefer a different image tag.)*

2.  **Run the Docker container (with Data Persistence):**
    The SQLite database (`users.db`) where user information is stored resides inside the Docker container. If you remove the container, this database file (and all user data) will be lost unless you persist it.

    To persist user data using a **named Docker volume**, run the following command. This maps port 2222 on your host to port 5000 (Flask) inside the container and ensures the database outlives the container:
    ```sh
    docker run -d -p 2222:5000 -v lego_user_data:/app/backend/instance --name lego-website-container lego-website
    ```
    *   **How this works:**
        *   `-v lego_user_data:/app/backend/instance`: This mounts a Docker named volume called `lego_user_data` to the `/app/backend/instance` directory inside the container (where `users.db` is stored).
        *   If the `lego_user_data` volume doesn't exist, Docker creates it automatically.
        *   Your `users.db` will now be stored in this volume on your host system.

    When the container starts (with or without a pre-existing volume):
    *   If the `lego_user_data` volume is new or empty, the application will create the `users.db` file within it.
    *   It will create the necessary database tables (if they don't already exist in `users.db`).
    *   It will create a default admin user (username: `admin`, password: `adminpassword`) if one doesn't already exist in the database.

    **To run without persistent data (data will be lost if container is removed):**
    If you don't need data persistence (e.g., for quick testing), you can omit the volume mount:
    ```sh
    docker run -d -p 2222:5000 --name lego-website-container lego-website
    ```

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

---

## Running with Podman

Podman is a daemonless container engine that provides a Docker-compatible command-line interface. You can use Podman to build and run this application as well. The commands are very similar to Docker.

1.  **Build the Podman image:**
    Open your terminal in the project root directory (where the `Dockerfile` is located) and run:
    ```sh
    podman build -t lego-website .
    ```

2.  **Run the Podman container (with Data Persistence):**
    To run the container with data persistence using a named volume, use the following command. This will map port 2222 on your host to port 5000 inside the container and persist the SQLite database.
    ```sh
    podman run -d -p 2222:5000 -v lego_user_data:/app/backend/instance:Z --name lego-website-container lego-website
    ```
    *   **Note on the `:Z` option:** The `:Z` appended to the volume mount (`-v ...:Z`) is often important for SELinux-enabled systems (like Fedora, CentOS, RHEL). It tells Podman to relabel the volume content so it's accessible to the container. If you are not on an SELinux system, or have it in permissive mode, you might not strictly need it, but it's good practice for broader compatibility.

    When the container starts (with or without a pre-existing volume):
    *   If the `lego_user_data` volume is new or empty, the application will create the `users.db` file within it.
    *   It will create the necessary database tables (if they don't already exist in `users.db`).
    *   It will create a default admin user (username: `admin`, password: `adminpassword`) if one doesn't already exist in the database.

    **To run without persistent data (data will be lost if container is removed):**
    ```sh
    podman run -d -p 2222:5000 --name lego-website-container lego-website
    ```

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:2222` (or `http://127.0.0.1:2222` if localhost does not work).

4.  **Access the Admin Page:**
    To manage users, navigate to `http://localhost:2222/admin`.
    You may need to log in using the main application's login page with the admin credentials (`admin`/`adminpassword`).

### Managing Podman Containers

*   **List running containers:**
    ```sh
    podman ps
    ```
*   **List all containers (including stopped):**
    ```sh
    podman ps -a
    ```
*   **View logs from a running container:**
    ```sh
    podman logs -f lego-website-container
    ```
*   **Stop a container:**
    ```sh
    podman stop lego-website-container
    ```
*   **Remove a container:**
    (Ensure it's stopped first)
    ```sh
    podman rm lego-website-container
    ```
*   **Manage Podman volumes:**
    *   List volumes: `podman volume ls`
    *   Inspect a volume: `podman volume inspect lego_user_data`
    *   Remove a volume: `podman volume rm lego_user_data` (be careful, this deletes the persisted data).

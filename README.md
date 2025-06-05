# Django User Management Application

This project is a user management application built with Django, providing REST APIs for user registration, login, and management. It is containerized using Docker/Podman.

## Features
* User registration
* Token-based authentication (Login/Logout using JWT)
* User detail retrieval and update
* Django Admin interface for user management

## Core Technologies
* Python
* Django
* Django REST Framework (for APIs)
* SimpleJWT (for token authentication)
* SQLite (default database)
* Gunicorn (WSGI server)
* Docker / Podman (for containerization)

## Setup and Running with Docker

### 1. Clone the Repository
```sh
git clone <repository_url>
cd <repository_directory_name>
```

### 2. Environment Configuration (.env file)
This application uses a `.env` file at the project root to manage environment-specific settings. Before building the Docker image, create a `.env` file in the project root with the following content:

```env
# Django settings
SECRET_KEY='your_strong_secret_key_here_please_change_me'
DEBUG=True
ALLOWED_HOSTS='*' # For development. For production, list your specific host(s), e.g., 'localhost,127.0.0.1,yourdomain.com'

# Database (defaults to SQLite in the project root /app/db.sqlite3 inside container)
DATABASE_URL='sqlite:///db.sqlite3'

# Logging
DJANGO_LOG_LEVEL='INFO'

# Add any other environment variables your application might need
```
**Important:**
* Replace `'your_strong_secret_key_here_please_change_me'` with a strong, unique secret key. You can generate one using Django's utilities if needed.
* For production, set `DEBUG=False` and configure `ALLOWED_HOSTS` appropriately.

### 3. Build the Docker Image
Open your terminal in the project root directory (where the `Dockerfile` is located) and run:
```sh
docker build -t django-auth-app .
```
*(You can use a different image tag like `lego-website` if you prefer.)*

### 4. Run the Docker Container

**With Data Persistence (Recommended):**
The SQLite database (`db.sqlite3`) where user information is stored resides at `/app/db.sqlite3` inside the Docker container. To persist this data, use a named Docker volume:

```sh
docker run -d -p 2222:8000 -v django_app_data:/app --name django-app-container django-auth-app
```
*   **Explanation:**
    *   `-d`: Runs the container in detached mode.
    *   `-p 2222:8000`: Maps port 2222 on your host to port 8000 (where Gunicorn runs) inside the container.
    *   `-v django_app_data:/app`: Mounts a Docker named volume called `django_app_data` to the `/app` directory inside the container. The `db.sqlite3` file will be stored here. If the volume doesn't exist, Docker creates it.
    *   `--name django-app-container`: Assigns a name to your container for easier management.
    *   `django-auth-app`: The name of the image you built.

**Without Data Persistence (Data lost if container is removed):**
```sh
docker run -d -p 2222:8000 --name django-app-container django-auth-app
```

### 5. Access the Application
*   **Web Interface (HTML pages):** Open your web browser and navigate to `http://localhost:2222`.
    *   Login page: `http://localhost:2222/login/`
    *   Registration page: `http://localhost:2222/registration/`
*   **API Endpoints (example):**
    *   Register: `POST http://localhost:2222/api/auth/register/`
    *   Login (get token): `POST http://localhost:2222/api/auth/login/`
    *   User Details (requires token): `GET http://localhost:2222/api/auth/user/`

### 6. Access the Django Admin Interface
*   Navigate to `http://localhost:2222/admin/`.
*   **Admin User:**
    *   If you migrated data from a previous version of this app that had an 'admin' user, that user should be available with `is_staff=True` and `is_superuser=True`. The password would be the same as before.
    *   To create a new superuser if one doesn't exist:
        ```sh
        docker exec -it django-app-container python manage.py createsuperuser
        ```
        Follow the prompts to set a username, email (optional), and password.

### Docker Container Management
*   **List running containers:** `docker ps`
*   **View logs:** `docker logs -f django-app-container`
*   **Stop container:** `docker stop django-app-container`
*   **Remove container:** `docker rm django-app-container` (ensure it's stopped first)
*   **Manage volumes:** `docker volume ls`, `docker volume inspect django_app_data`, `docker volume rm django_app_data` (careful, this deletes persisted data).

---

## Setup and Running with Podman

Podman is a daemonless container engine. The commands are very similar to Docker.

### 1. Clone the Repository (Same as Docker)
### 2. Environment Configuration (.env file) (Same as Docker)

### 3. Build the Podman Image
```sh
podman build -t django-auth-app .
```

### 4. Run the Podman Container

**With Data Persistence:**
```sh
podman run -d -p 2222:8000 -v django_app_data:/app:Z --name django-app-container django-auth-app
```
*   **Note on `:Z`:** The `:Z` option is often important for SELinux systems (Fedora, CentOS, RHEL) to relabel volume content for container access.

**Without Data Persistence:**
```sh
podman run -d -p 2222:8000 --name django-app-container django-auth-app
```

### 5. Access the Application (Same as Docker)
### 6. Access the Django Admin Interface (Same as Docker)
*   To create a superuser with Podman:
    ```sh
    podman exec -it django-app-container python manage.py createsuperuser
    ```

### Podman Container Management (Commands are similar to Docker, just replace `docker` with `podman`)
*   **List running containers:** `podman ps`
*   **View logs:** `podman logs -f django-app-container`
*   **Stop container:** `podman stop django-app-container`
*   **Remove container:** `podman rm django-app-container`
*   **Manage volumes:** `podman volume ls`, etc.

# Use an official Nginx runtime as a parent image
FROM nginx:alpine

# Set the working directory in the container
WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy all the local files from the current directory into the Nginx html directory
COPY . .

# Inform Docker that the container is listening on port 80
EXPOSE 80

# Command to run Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]

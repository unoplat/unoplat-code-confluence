# Stage 1: Build the Vite project using Node 20 and Yarn
FROM node:20 AS builder

# Set working directory inside the container
WORKDIR /src

# Copy package.json and yarn.lock to leverage Docker cache for dependencies
COPY package.json yarn.lock ./

# Install dependencies using Yarn
RUN yarn install

# Copy the rest of the project files
COPY . .

# Build the Vite project (assumes that "build" is defined in package.json scripts)
RUN yarn build

# Stage 2: Serve the built files using Nginx
FROM nginx:alpine

# Copy the built files from the builder stage to the Nginx html directory
COPY --from=builder /src/dist /usr/share/nginx/html

# Expose port 3000 for the web server
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
# Stage 1: Build the Vite project using Bun
FROM oven/bun:1.3.1 AS builder

# Set working directory inside the container
WORKDIR /src

# Copy package.json and bun.lock first to leverage Docker cache for dependencies
COPY package.json bun.lock ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy the rest of the project files
COPY . .

# Build the Vite project using production configuration
RUN bun run build --mode prod

# Stage 2: Serve the built files using Nginx
FROM nginx:alpine

# Copy the built files from the builder stage to the Nginx html directory
COPY --from=builder /src/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for the web server
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]

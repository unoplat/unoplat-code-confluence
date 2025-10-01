# Stage 1: Build the Vite project using Node 20 and Yarn
FROM node:20 AS builder

# Set working directory inside the container
WORKDIR /src

# Copy package.json first to leverage Docker cache for dependencies
COPY package.json yarn.lock ./

# Copy .yarn directory from local filesystem
COPY .yarnrc.yml ./
COPY .yarn ./.yarn

# Enable Corepack to manage Yarn version
RUN corepack enable

# Install dependencies
RUN yarn cache clean && yarn install --refresh-lockfile

# Copy the rest of the project files
COPY . .

# Build the Vite project using production configuration
RUN yarn build --mode prod

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

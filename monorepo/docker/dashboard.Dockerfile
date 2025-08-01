FROM nginx:alpine

# Copy the dashboard files
COPY dashboard/index.html /usr/share/nginx/html/index.html

# Configure nginx to serve on port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
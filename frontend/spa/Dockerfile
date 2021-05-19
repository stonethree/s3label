FROM node:latest

COPY . /home/spa
WORKDIR /home
RUN npm i source-map-resolve webpack-cli webpack-dev-server
WORKDIR /home/spa
RUN npm install

# ENTRYPOINT [ "npm", "run", "dev" ]
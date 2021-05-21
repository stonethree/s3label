FROM node
WORKDIR /home
# RUN npm i source-map-resolve
COPY . /home/spa
WORKDIR /home/spa
RUN npm i webpack-cli webpack-dev-server
RUN npm install

ENTRYPOINT [ "npm", "run", "dev" ]
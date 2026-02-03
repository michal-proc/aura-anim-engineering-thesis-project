FROM node:20

WORKDIR /usr/src/service/

COPY . .

EXPOSE 3000
ENTRYPOINT ["/bin/sh", "-c", "yarn && yarn dev --hostname 0.0.0.0 --port 3000"]
FROM alpine:latest  

RUN apk --no-cache add ca-certificates

WORKDIR /usr/src/app
COPY ./ /usr/src/app

EXPOSE 8080

CMD ./slow_app/slow_app
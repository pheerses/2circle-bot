FROM golang:1.22 AS builder

WORKDIR /app
COPY . .
RUN go build -o processor

FROM golang:1.22

RUN apt update && apt install -y --no-install-recommends ffmpeg && apt clean

WORKDIR /app
COPY --from=builder /app/processor .

CMD ["./processor"]

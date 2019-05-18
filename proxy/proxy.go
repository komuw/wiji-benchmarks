package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"
)

/*
CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o proxy/slow_app proxy/proxy.go
*/

func handler(w http.ResponseWriter, r *http.Request) {
	/*
	   start a server that has simulated latency
	*/
	rand.Seed(time.Now().UnixNano())
	min := 100
	max := 400
	n := rand.Intn(max-min) + min
	time.Sleep(time.Duration(n) * time.Millisecond)
	fmt.Fprintf(w, "Hello %d", n)
}

func main() {
	http.HandleFunc("/", handler)
	log.Println("listening on port 8080 ...")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("\n ListenAndServe failed", err)
	}
}

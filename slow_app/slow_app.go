package main

import (
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"time"
)

/*
1. run:
  go run slow_app/slow_app.go

2. build:
  CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o slow_app/slow_app slow_app/slow_app.go
*/

func slowHandler(w http.ResponseWriter, r *http.Request) {
	/*
	   path that has simulated latency
	*/
	rand.Seed(time.Now().UnixNano())
	min := 100
	max := 400
	n := rand.Intn(max-min) + min
	time.Sleep(time.Duration(n) * time.Millisecond)
	fmt.Fprintf(w, "latency: %dms", n)
}


func okayHandler(w http.ResponseWriter, r *http.Request) {
	/*
	   path that has no latency
	*/
	fmt.Fprint(w, "okay")
}

func main() {
	http.HandleFunc("/okay", okayHandler)
	http.HandleFunc("/slow", slowHandler)


	log.Println("listening on port 8080 ...")
	err := http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("\n ListenAndServe failed", err)
	}
}

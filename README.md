## wiji-benchmarks     
[![CircleCI](https://circleci.com/gh/komuw/wiji-benchmarks.svg?style=svg)](https://circleci.com/gh/komuw/wiji-benchmarks)  


### What:
This benchmark, show how [`wiji`](https://github.com/komuw/wiji) performs when executing different types of tasks/workloads.  

This benchmark does the following:  
- It queues about 100,000(100K) network IO bound tasks. Each of these tasks makes a newtwork request to a backend with a latency that varies between 100 and 400 milliseconds.    
- It queues about 100,000 disk IO bound tasks. Each of these tasks creates a random file, generates a random 16KB text, opens the file, writes that 16KB text to it & closes that file  and then finally it deletes that file.   
  16KB is approximately the same size as the novel; [`The Raven` by `Edgar Allan Poe`](https://en.wikipedia.org/wiki/The_Raven)
- It queues about 100,000 CPU bound tasks. Each of these tasks generates a 16KB text, does blake2 hash of it, encrypts the text and then decrypts it.   
- It queues about 100,000 memory bound tasks. Each of these tasks calculates how much free RAM there is, then stores something in RAM that is equal to 10% of the free RAM.    
- It queues about 100,000 tasks each of which adds two numbers together.   
- It queues about 100,000 tasks each of which performs division of two numbers.   

- It dequeues and executes all the above tasks.   

- All these operations happen concurrently.   


### Usage:

You can run this benchmarks/examples using either on a Redis broker or [`wijisqs`](https://github.com/komuw/wijisqs) which is a `wiji` broker that uses [AWS SQS](https://aws.amazon.com/sqs/).     

The broker in use(redis or SQS) is controlled via environment variables.     
The environment variables are stored in the file called `compose.env`     

By default, when you `docker-compose up`, the benchmarks is run using the redis broker included in this repo.    
To use AWS SQS, edit `compose.env` so as to set the environment variable `USE_SQS=YES` additionally the environment variables; `AWS_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` should be set to appropriate values based on your AWS account.    

Once you have set the neccessary environment variables, run:     
```bash
docker-compose up
```    

### Results:
The benchmark was run on a $5/month digitalocean server with 1GB of RAM and 1 cpu.    
The server was located in San francisco.   
The broker in use was [`wijisqs`](https://github.com/komuw/wijisqs) which is a `wiji` broker that uses [AWS SQS](https://aws.amazon.com/sqs/).    
The SQS broker was located in Ireland(eu-west-1).    
The ping latency between digitalocean Sanfrancisco and AWS Ireland was about `152 ms`  

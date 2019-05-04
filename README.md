## wiji-benchmarks         

This benchmark, show how `wiji` performs when executing different types of tasks/workloads.   

You can run this benchmarks/examples either on a Redis broker or using AWS SQS broker.     

The broker in use(redis or SQS) is controlled via environment variables.     
The environment variables are stored in the file called `compose.env`     

By default, when you `docker-compose up`, the benchmarks is run using the redis broker included in this repo.    
To use AWS SQS, edit `compose.env` so as to set the environment variable `USE_SQS="YES"` and also the environment variables; `AWS_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` should be set to appropriate values based on your AWS account.    


run:     
```bash
docker-compose up --build
```    


This benchmark does the following:  
- It queues about 10K network IO bound task. Each of these tasks makes a newtwork request to a backend that has a latency that varies between 2 and 7 seconds. The backend in question is `https://httpbin.org/delay/{latency}`    
- It queues about 10K disk IO bound tasks. Each of these tasks creates a random file, generates a random 16KB text,  opens the file, writes that 16KB text to it & closes that file  and then finally it deletes that file.  
- It queues about 10K CPU bound tasks. Each of these tasks generates a 16KB text, does blake2 hash of it, encrypts the text and then decrypts it.   
- It queues about 10K RAM(memory) bound tasks. Each of these tasks calculates how much free RAM there is, then stores something in RAM that is equal to 10% of the free RAM.    
- It queues about 10K tasks each of which adds two numbers together.   
- It queues about 10K tasks each of which performs division of two numbers.   

- It dequeues and executes all the above tasks.   

- All these operations happen concurrently.   


stats:
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}\t"
```
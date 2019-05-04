## wiji-benchmarks        

You can run this benchmarks/examples either on a Redis broker or using AWS SQS broker.     

The broker in use(redis or SQS) is controlled via environment variables.     
The environment variables are stored in the file called `compose.env`     

By default, when you `docker-compose up`, the benchmarks is run using the redis broker included in this repo.    
To use AWS SQS, edit `compose.env` so as to set the environment variable `USE_SQS="YES"` and also the environment variables; `AWS_REGION_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` should be set to appropriate values based on your AWS account.    


run:     
```bash
docker-compose up --build
```    


stats:
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}\t"
```
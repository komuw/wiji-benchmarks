## wiji-benchmarks        

run:     
```bash
docker-compose up --build
```    


stats:
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}\t{{.PIDs}}\t"
```
# Apache Spark

When a Spark Job is triggered, the following things happen:

1. Job is submitted to Master Node via `spark-submit` action  
2. Master Node houses cluster manager required for Spark  
3. Master Node initialises a Spark Driver container on one of the worker nodes  
4. Master Node also initialises a number of Spark Executor containers on one or more worker nodes (depends on `spark-job-config`)  
5. Driver initialises PySpark and JVM drivers and calls main function of Application Code  
6. Driver interacts with Executors to run the program  
7. Results are aggregated back into Driver after processing  
8. Results are stored by Driver  
9. Driver and Executors shut down and resources are released.  

## A Typical Spark Cluster

![Spark Cluster Architecture](./spark-cluster.drawio.png)

[How Apache Spark Works](./apache-spark/how-apache-spark-works.md)

[Transformations and Actions](./apache-spark/transformations-and-actions.md)

[Jobs, Stages and Tasks](./apache-spark/jobs-stages-tasks.md)

[Resource Utilization](./apache-spark/resource-utilization.md)

[Spark Executor Container Memory Allocation](./apache-spark/spark-executor-container-memory-allocation.md)

# Apple Orders API

A simple Flask REST API that simulates an ordering system for Apple products.  
This project is part of the final assignment for the DevOps course.

## Features

- GET /products – Returns a list of available products
- POST /order – Allows placing an order and updates product stock
- Products include: SKU, name, storage, connectivity, colour, and stock

## Requirements

- Docker installed
- Git installed

## How to Run the Application

1. Clone the repository:  
   git clone https://github.com/idanga41/apple-orders.git  
   cd apple-orders

2. Run the app using the Docker image from Docker Hub:  
   docker run -p 5000:5000 idanga41/apple-orders-app:v1

3. Test the API:

   Home route:  
   curl http://localhost:5000/

   Get product list:  
   curl http://localhost:5000/products

   Place an order:  
   curl -X POST http://localhost:5000/order \
     -H "Content-Type: application/json" \
     -d '{"sku": "APL-IPH15-256-BLK", "customer_name": "Tester"}'

## Project Files

- app.py – Flask application code
- requirements.txt – Python dependencies
- Dockerfile – Docker image definition
- spec.txt – Project specification
- apple-deployment.yaml – Kubernetes Deployment file (bonus)
- apple-service.yaml – Kubernetes LoadBalancer Service (bonus)

## Kubernetes (Bonus - Optional)

1. Start Minikube cluster with 3 nodes:  
   minikube start -p apple-orders-cluster --nodes 3

2. Install CA certificates on all nodes (if required):  
   ~/k8s/2-pod-and-containers/1-basic-pod-and-deployment-demo/single-pod/install-ca-on-nodes.sh apple-orders-cluster

3. Deploy the application:  
   kubectl apply -f apple-deployment.yaml

4. Expose with LoadBalancer:  
   kubectl apply -f apple-service.yaml

5. Access the service:  
   minikube service apple-orders-service -p apple-orders-cluster

# Apple Orders API

A simple Flask-based API for managing Apple product orders. Deployed using Docker and Kubernetes via Minikube.

---

## Features

- REST API with endpoints to:
  - View products (`/products`)
  - Place an order (`/order`)
- Built with Flask 3.1
- Containerized with Docker
- Deployed to Kubernetes (via Minikube)
- Exposed using a LoadBalancer (`minikube tunnel`)

---

## Project Structure

apple-orders/
├── app.py
├── requirements.txt
├── Dockerfile
├── k8s/
│   ├── flask-deployment.yaml
│   └── flask-service.yaml
└── README.md

---

## Deployment on Kubernetes

### 1. Build & Push Docker image

    docker build -t idanga41/apple-orders-app:v3 .
    docker push idanga41/apple-orders-app:v3

### 2. Apply Deployment & Service

    kubectl apply -f k8s/flask-deployment.yaml
    kubectl apply -f k8s/flask-service.yaml

### 3. Run tunnel to access LoadBalancer

    minikube tunnel -p fournodes

Then open in browser:

    http://<EXTERNAL-IP>

---

## Endpoints

- `GET /` — Health check: returns welcome message  
- `GET /products` — List available products  
- `POST /order` — Place an order with JSON body:  
  {
    "sku": "product_sku",
    "customer_name": "Your Name"
  }

---

## To do

- Add persistent storage  
- Add PostgreSQL integration  
- Add authentication  
- Add unit tests  
- Add CI/CD pipeline

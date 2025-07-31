# Apple Orders API

This is a simple Flask-based REST API for managing Apple product orders. It allows viewing available Apple products and placing orders while updating stock levels.

## How to Run the Project After Cloning

1. Clone the repository:

```bash
git clone https://github.com/idanga41/apple-orders.git
cd apple-orders
```

2. Build the Docker image:

```bash
docker build -t apple-orders-app .
```

3. Run the Docker container and expose port 5000:

```bash
docker run -p 5000:5000 apple-orders-app
```

4. Access the API using this URL:

```
http://localhost:5000
```

## API Endpoints

### GET /products

Returns a list of all available Apple products.

Example:
```bash
curl http://localhost:5000/products
```

### POST /order

Places an order and decreases stock by 1 if the product is available.

Example:
```bash
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{"sku": "APL-IPH15-256-BLK", "customer_name": "Alice"}'
```

## Docker Notes

- The image exposes port 5000 inside the container.
- Flask app is configured to run on `host="0.0.0.0"` so it can be accessed externally via `localhost:5000`.

## Kubernetes (Bonus)

If running with Kubernetes (e.g., Minikube), make sure:

- The image `idanga41/apple-orders-app:v4` is used in the deployment YAML
- You run a LoadBalancer service (`apple-service.yaml`)
- You access the service using the URL provided by:

```bash
minikube service apple-orders-service --url
```

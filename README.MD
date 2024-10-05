# Inventory and Sales Management API

A comprehensive RESTful API built with FastAPI for managing products, sales, inventory, and generating detailed reports. This application includes user authentication, product management, sales recording with automatic stock updates, receipt generation, discount and promotion handling, and various reporting functionalities.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [User Management](#user-management)
  - [Product Management](#product-management)
  - [Sales Management](#sales-management)
  - [Reporting](#reporting)
  - [Promotions](#promotions)
- [Usage Examples](#usage-examples)
- [Considerations](#considerations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication**: Secure login using OAuth2 with password flow.
- **Product Management**: Create, update, and manage product inventory.
- **Sales Recording**: Register sales, apply discounts, and automatically update stock levels.
- **Receipt Generation**: Generate detailed receipts for each sale.
- **Discounts and Promotions**: Apply specific discounts or promotions to products.
- **Reporting**: Generate detailed sales reports, current stock levels, and historical stock movements.
- **In-Memory Data Storage**: Quick setup using in-memory data structures (suitable for development and testing).

## Prerequisites

- **Python 3.8+**: Ensure you have Python installed. You can download it from [here](https://www.python.org/downloads/).
- **pip**: Python package installer (comes with Python).
- **Git**: For cloning the repository (optional).

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/pudimKBM/Gerenciador_Estoque.git
   cd Gerenciador_Estoque
   ```

   *Alternatively, you can download the repository as a ZIP file and extract it.*

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**

   - **On Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **On macOS and Linux:**

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   *If `requirements.txt` is not provided, install the necessary packages manually:*

   ```bash
   pip install fastapi uvicorn passlib[bcrypt] python-multipart
   ```

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

- **`main`**: Refers to the `main.py` file.
- **`app`**: The FastAPI instance.
- **`--reload`**: Enables auto-reloading on code changes (useful during development).

The server will start at `http://127.0.0.1:8000/`.

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI**: Accessible at `http://127.0.0.1:8000/docs`
- **ReDoc**: Accessible at `http://127.0.0.1:8000/redoc`

Use these interfaces to explore and test the API endpoints.

## Authentication

The API uses OAuth2 with password flow for authentication.

1. **Obtain an Access Token**

   - Send a `POST` request to `/token` with form data containing `username` and `password`.

   ```bash
   curl -X POST "http://127.0.0.1:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=user1&password=secret"
   ```

   - **Response:**

     ```json
     {
       "access_token": "user1",
       "token_type": "bearer"
     }
     ```

2. **Use the Access Token**

   - Include the token in the `Authorization` header for protected endpoints.

   ```bash
   Authorization: Bearer user1
   ```

*Note: In the current implementation, the access token is simply the username. For a production environment, consider using JWT tokens for enhanced security.*

## API Endpoints

### User Management

- **Create a New User**

  - **Endpoint:** `POST /usuarios/`
  - **Description:** Register a new user.
  - **Request Body:**

    ```json
    {
      "username": "user2",
      "password": "mypassword",
      "full_name": "User Two",
      "email": "user2@example.com",
      "disabled": false
    }
    ```

- **List All Users**

  - **Endpoint:** `GET /usuarios/`
  - **Description:** Retrieve a list of all registered users.
  - **Authentication:** Required

### Product Management

- **Register a New Product**

  - **Endpoint:** `POST /produtos/`
  - **Description:** Add a new product to the inventory.
  - **Request Body:**

    ```json
    {
      "nome": "Product A",
      "codigo": "P001",
      "categoria": "Category X",
      "quantidade": 100,
      "preco": 50.0,
      "descricao": "Description of Product A",
      "fornecedor": "Supplier X"
    }
    ```

  - **Authentication:** Required

- **Add to Product Stock**

  - **Endpoint:** `PUT /produtos/{codigo}/adicionar`
  - **Description:** Add quantity to an existing product's stock.
  - **Path Parameter:** `codigo` - Product code
  - **Query Parameter:** `quantidade` - Quantity to add
  - **Authentication:** Required

- **Remove from Product Stock**

  - **Endpoint:** `PUT /produtos/{codigo}/remover`
  - **Description:** Remove quantity from an existing product's stock.
  - **Path Parameter:** `codigo` - Product code
  - **Query Parameter:** `quantidade` - Quantity to remove
  - **Authentication:** Required

- **Update Product Stock**

  - **Endpoint:** `PUT /produtos/{codigo}/atualizar`
  - **Description:** Set a specific quantity for a product's stock.
  - **Path Parameter:** `codigo` - Product code
  - **Query Parameter:** `quantidade` - New stock quantity
  - **Authentication:** Required

- **Low Stock Alert**

  - **Endpoint:** `GET /produtos/alerta`
  - **Description:** Retrieve products with low stock (quantity < 5).
  - **Authentication:** Required

### Sales Management

- **Register a Sale**

  - **Endpoint:** `POST /vendas/`
  - **Description:** Record a new sale, apply discounts, and update stock.
  - **Request Body:**

    ```json
    {
      "items": [
        {
          "codigo": "P001",
          "quantidade": 2,
          "preco_unitario": 50.0,
          "desconto": 10.0
        },
        {
          "codigo": "P002",
          "quantidade": 1,
          "preco_unitario": 100.0,
          "desconto": 0.0
        }
      ],
      "desconto_total": 5.0
    }
    ```

  - **Authentication:** Required

### Reporting

- **Sales Report**

  - **Endpoint:** `GET /relatorios/vendas/`
  - **Description:** Retrieve a detailed report of all sales.
  - **Authentication:** Required

- **Stock Report**

  - **Endpoint:** `GET /relatorios/estoque/`
  - **Description:** View current stock levels of all products.
  - **Authentication:** Required

- **Stock Movements History**

  - **Endpoint:** `GET /relatorios/movimentacoes/`
  - **Description:** Get a history of all stock additions and removals.
  - **Authentication:** Required

### Promotions

- **Create a Promotion**

  - **Endpoint:** `POST /promocoes/`
  - **Description:** Define a new promotion.
  - **Request Body:**

    ```json
    {
      "codigo": "PROMO10",
      "descricao": "10% off on selected items",
      "desconto_percentual": 10.0
    }
    ```

  - **Authentication:** Required

- **List All Promotions**

  - **Endpoint:** `GET /promocoes/`
  - **Description:** Retrieve all available promotions.
  - **Authentication:** Required

## Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://127.0.0.1:8000/usuarios/" \
-H "Content-Type: application/json" \
-d '{
  "username": "user2",
  "password": "mypassword",
  "full_name": "User Two",
  "email": "user2@example.com",
  "disabled": false
}'
```

### 2. Obtain an Access Token

```bash
curl -X POST "http://127.0.0.1:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=user1&password=secret"
```

### 3. Add a New Product

```bash
curl -X POST "http://127.0.0.1:8000/produtos/" \
-H "Authorization: Bearer user1" \
-H "Content-Type: application/json" \
-d '{
  "nome": "Product A",
  "codigo": "P001",
  "categoria": "Category X",
  "quantidade": 100,
  "preco": 50.0,
  "descricao": "Description of Product A",
  "fornecedor": "Supplier X"
}'
```

### 4. Register a Sale

```bash
curl -X POST "http://127.0.0.1:8000/vendas/" \
-H "Authorization: Bearer user1" \
-H "Content-Type: application/json" \
-d '{
  "items": [
    {
      "codigo": "P001",
      "quantidade": 2,
      "preco_unitario": 50.0,
      "desconto": 10.0
    },
    {
      "codigo": "P002",
      "quantidade": 1,
      "preco_unitario": 100.0,
      "desconto": 0.0
    }
  ],
  "desconto_total": 5.0
}'
```
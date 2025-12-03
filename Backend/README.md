

### Prerequisites
Ensure you have the following installed:

- Python >= 3.10
- PostgreSQL

 

Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```


Run database migrations to initialize the database schema:
    ```bash
    alembic revision --autogenerate -m "init"
    alembic upgrade head
    ```

## Running the Application

```bash
fastapi dev src/
```


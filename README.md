# fastapi + sqlalchemy 


## Description

this project expose crud operations over REST for Employee resource 

## Installation
- Navigate to the project directory 
- Create a new virtual env `python -m venv venv`
- Activate the virtual env `source venv/bin/activate`
- Install the requirements `pip install -r requirements.txt`
- alembic setup (DB):
  - alembic revision --autogenerate -m "initialize"
  - alembic upgrade head
### Requirements

- Python 3.10 or later
- [Alembic](https://alembic.sqlalchemy.org/en/latest/installation.html)

## Running the project
- create a `.env` file and place it on the root of the project and add the following env (if needed) 
  - APP_PORT - default on 5000 - you may change it to any available port 
  - SWAGGER_API_KEY - apiKey for using swagger (default 1234567)
- python main.py

## Running tests
- Activate the virtual env `source myenv/bin/activate`
- run `pytest`

## Swagger
after the project is running, you may use swagger - go to http://localhost:5000/docs?apiKey=1234567


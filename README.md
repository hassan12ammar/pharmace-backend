# BASBOS
## Django/Django Ninja Backend
This is a backend application built using Django and Django Ninja. It provides a RESTful API for interacting with your data and can be easily integrated into your frontend or mobile application.

## Features
Authentication and authorization using JWT
RESTful API for data management
Easy integration with Django admin

## Installation and Setup

### Clone the repository
```sh
git clone https://github.com/hassan12ammar/basbos-backend.git
```
```sh
cd basbos-backend
```

### Create a virtual environment and activate it:
```sh
python -m venv basbos_venv
```
```sh
source basbos_venv/bin/activate
```
#### if you use **fish**
```sh
$ source dna101blog_venv/bin/activate.fish
```

### Install dependencies
``` sh
pip install -r requirements.txt
```

### Run migrations
``` sh
python manage.py migrate
```

### Start the server
``` sh
python manage.py runserver
```

## API Documentation
API documentation is available at http://localhost:8000/api/docs. You can use the Swagger UI to explore the API and test endpoints.

## License
This project is licensed under the MIT License. Feel free to use and modify it as per your requirements.

## Contributing
Contributions are welcome! If you have any feature requests, bug reports, or pull requests, please feel free to open an issue or a pull request.

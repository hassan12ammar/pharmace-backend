# Pharmaceutical 
Pharmaceutical is an e-commerce website backend that serves as an online marketplace for pharmacies to sell their drugs.The website aims to provide a convenient and reliable platform for pharmacies to reach a wider audience and for customers to easily purchase their medications online.

## Django/Django Ninja Backend
The website is built with Django and uses NinjaAPI to handle the RESTful API. The website includes features such as user authentication, profile management, pharmacy listing and search, drug managment, and cart management. It also has a review system where users can rate and review the pharmacies they have purchased from. It provides a RESTful API for interacting with your data and can be easily integrated into your frontend or mobile application.

## Features
* Authentication and authorization using JWT
* RESTful API for data management
* Admin panel with friendly interface

## Installation and Setup

### Clone the repository
```sh
git clone https://github.com/hassan12ammar/pharmace-backend.git
```
```sh
cd pharmace-backend
```

### Create a virtual environment and activate it:
```sh
python -m venv pharmace_venv
```
```sh
source pharmace_venv/bin/activate
```
##### if you use **fish**
```sh
$ source pharmace_venv/bin/activate.fish
```
##### if you use **Windows**
```sh
source source pharmace_venv\Scripts\activate
```

### Install dependencies
``` sh
pip install -r requirements.txt
```

### Run migrations
``` sh
python manage.py migrate
```

### Create super user to access the Admin Panel
``` sh
python manage.py createsuperuser
```

### Start the server
``` sh
python manage.py runserver
```

## API Documentation
API documentation is available at http://localhost:8000/api/docs. You can use the Swagger UI to explore the API and test endpoints.

## Admin Panel
The admin panel is available at http://localhost:8000/admin. You can use it to manage the database and perform CRUD operations on the models. The admin panel is only accessible to superusers.

## License
This project is licensed under the MIT License. Feel free to use and modify it as per your requirements.

## Contributing
Contributions are welcome! If you have any feature requests, bug reports, or pull requests, please feel free to open an issue or a pull request.

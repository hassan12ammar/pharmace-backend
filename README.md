# Pharmaceutical 
Pharmaceutical is an e-commerce website backend that serves as an online marketplace for pharmacies to sell their drugs.The website aims to provide a convenient and reliable platform for pharmacies to reach a wider audience and for customers to easily purchase their medications online.
<br> <br>

# Django/Django Ninja Backend
The website is built with Django framework and uses Django Ninja to handle the RESTful API. The website includes features such as user authentication, profile management, pharmacy listing and Search by Drug Name and Pharmacy Name, drug managment, and cart management. It also has a review system where users can rate and review the pharmacies they have purchased from. It provides a RESTful API for interacting with your data and can be easily integrated into your frontend or mobile application.

## Features of Django/Django Ninja
* Authentication and authorization using JWT
* RESTful API for data management
* Admin panel with friendly interface
<br> <br>

# Key Features

## User Authentication and Profile Management
Pharmaceutical provides a robust user authentication system using JSON Web Tokens (JWT). Users can sign up, sign in, and manage their profiles. This ensures secure access to the website and personalized experiences for each user.

## Pharmacy Listing and Search Functionality
The website enables pharmacies to list their products, including drugs, with detailed information such as name, description, price, and availability. Customers can easily search for pharmacies based on drug names or pharmacy names, making it convenient to find the desired medications or preferred pharmacies.

## Drug Management
Pharmaceutical offers drug management capabilities, allowing pharmacies to add, edit, and manage their drug inventory. This ensures accurate and up-to-date information about available medications for customers.

## Cart Management
The website provides a user-friendly cart management system, allowing customers to add drugs to their carts, increment or decrease quantities, and remove items as needed. This simplifies the ordering process and provides a smooth shopping experience.

## Review System
Pharmaceutical incorporates a review system where customers can rate and write reviews for the pharmacies they have purchased from. This feature helps build trust and transparency within the platform, allowing users to make informed decisions based on feedback from others.

## Admin Panel with Friendly Interface
The project includes an admin panel with a user-friendly interface. It allows administrators to manage various aspects of the website, such as user profiles, pharmacies, drugs, and reviews. The admin panel simplifies administrative tasks and provides convenient control over the platform.

## RESTful API
Pharmaceutical offers a RESTful API for seamless integration with frontend applications or mobile applications. The API follows industry best practices and allows developers to interact with the website's data, perform CRUD operations, and build custom interfaces.

With its comprehensive features, Pharmaceutical provides a solid foundation for building a successful online pharmaceutical marketplace. Whether you are a pharmacy owner or a developer looking to create an e-commerce platform, Pharmaceutical can be easily customized and extended to meet your specific requirements.
<br> <br>

# Installation and Setup

## if you are lazy to do the below
```sh
./first_start.sh
```

## Clone the repository
```sh
git clone https://github.com/hassan12ammar/pharmace-backend.git
```
```sh
cd pharmace-backend
```

## Create a virtual environment and activate it:
```sh
python -m venv pharmace_venv
```
```sh
source pharmace_venv/bin/activate
```
#### if you use **fish**
```sh
$ source pharmace_venv/bin/activate.fish
```
#### if you use **Windows**
```sh
source source pharmace_venv\Scripts\activate
```

## Install dependencies
``` sh
pip install -r requirements.txt
```

## Make migrations
``` sh
python manage.py makemigrations
```

## Run migrations
``` sh
python manage.py migrate
```

## Create super user to access the Admin Panel
``` sh
python manage.py createsuperuser
```

## Start the server
``` sh
python manage.py runserver
```
<br>

# API Documentation
API documentation is available at http://localhost:8000/api/docs. You can use the Swagger UI to explore the API and test endpoints.
<br>

# Admin Panel
The admin panel is available at http://localhost:8000/admin. You can use it to manage the database and perform CRUD operations on the models. The admin panel is only accessible to superusers.
<br>

# License
This project is licensed under the MIT License. Feel free to use and modify it as per your requirements.
<br>

# Contributing
Contributions are welcome! If you have any feature requests, bug reports, or pull requests, please feel free to open an issue or a pull request.

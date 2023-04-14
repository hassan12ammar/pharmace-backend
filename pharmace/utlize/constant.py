#Import the required dependencies
import os
from dotenv import load_dotenv

#Load environment variables from .env file
load_dotenv()

#Get specific environment variables
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = bool(os.environ['DEBUG'])
# general constants
DESCRIPTION="Pharmaceutical is a backend API for an e-commerce website for pharmacies. \
    The API is built using Django and Django Ninja and allows users to perform various operations\
        related to authentication, user profiles, pharmacies, drugs, and shopping cart management."

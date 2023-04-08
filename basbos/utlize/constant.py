#Import the required dependencies
import os
from dotenv import load_dotenv

#Load environment variables from .env file
load_dotenv()

#Get specific environment variables
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = bool(os.environ['DEBUG'])

# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     SECRET_KEY = os.getenv("SECRET_KEY")

#     # ✅ SQLAlchemy connection for MySQL
#     SQLALCHEMY_DATABASE_URI = (
#         f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
#         f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
#     )
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     # ✅ Cloudinary configuration
#     CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
#     CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
#     CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    # MySQL / SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
        f"/{os.getenv('MYSQL_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB / MongoEngine
    # if you have a single-URI in env:
    MONGODB_SETTINGS = {
        "host": os.getenv("MONGO_URI")
    }

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY   = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET= os.getenv("CLOUDINARY_API_SECRET")

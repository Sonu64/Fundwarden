from app.app import create_app
import os
from dotenv import load_dotenv

# Manually load the .env file
load_dotenv()

app = create_app()

if __name__ == "__main__":
    app.run(debug = True)
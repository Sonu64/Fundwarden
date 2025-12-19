from app.app import create_app

fundwarden_app = create_app()

if __name__ == "__main__":
    fundwarden_app.run(debug=True)
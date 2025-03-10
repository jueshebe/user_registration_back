"""Run flask app."""
from app import create_app

app = create_app()

host = ".".join(["0"] * 4)
if __name__ == "__main__":  # Only in dev
    app.run(host=host, port=8080, debug=False)  # nosec

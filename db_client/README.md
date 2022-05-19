Python client to upload data to the public MySQL database.

## How to set it up?

Virtual environments using **venv**: https://docs.python.org/3/library/venv.html
Dependency management with **poetry**: https://python-poetry.org/docs/#installation

Set up project interpreter:

```bash
# Create a virtual environment (a local copy of python)
python3.10 -m venv .venv

# Switch to the virtual environment
source .venv/bin/activate

# Install dependencies
poetry install
```

<br/>

## How to run it?

1. Use the file `config.example.json` to create a file `config.json` for your setup

2. Run it with (using the virtual env from before):

    ```bash
    python main.py
    ```

3. Modify the `main.py` code for your usecase. Ask Moritz Makowski for user accounts and other databases.

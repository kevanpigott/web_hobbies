# Web Hobbies

This project is a Flask web application for managing user hobbies. It includes features such as user authentication, hobby management, and viewing popular hobbies.

## Setup

### Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Installing Poetry

If you don't have Poetry installed, you can install it using the following command:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

### Setting Up the Project

1. Clone the repository:

```sh
git clone https://github.com/kevanpigott/web_hobbies.git
cd web_hobbies
```

2. Install poetry
```sh
python -m pip install poetry
```

3. Install remaining requirements
```sh
poetry install
```

### Activating the Virtual Environment
To activate the virtual environment, use the following command:
```sh
source .venv/bin/activate
```

On Windows, use:
```sh
.venv\Scripts\activate
```

### Running the Application
To run the Flask application, use the ```poe``` command provided by Poetry. The poe command is a shortcut for running tasks defined in the ```pyproject.toml``` file.

Start the Flask development server in debug mode:
```sh
poe run
```
This command will start the Flask development server on http://127.0.0.1:5000 with debug mode enabled.

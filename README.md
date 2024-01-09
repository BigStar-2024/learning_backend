# learning-backend

This project contains the backend for Learn With Socrates

## Requirements

- Python 3.8
- [Pipenv](https://github.com/pypa/pipenv#installation)



## Basic Installation

1. Clone the repository:

    - Using HTTPS
    ```sh
    git clone https://github.com/WithSocrates/learning_backend.git
    ```

    - Using SSH
    ```sh
    git clone git@github.com:WithSocrates/learning_backend.git
    ```

2. Change directory into `learning_backend`:

```sh
cd learning_backend
```

3. Install dependencies from Pipfile:

```sh
pipenv install
```

4. Place `env.py` inside `src/app/settings/`

## Usage

1. Activate the project virtualenv:

```sh
pipenv shell
```

2. Create tables in the DB by migrating:

```sh
python src/manage.py migrate
```

3. Create an admin user:

```sh
python src/manage.py createsuperuser
```

4. Start the developement server

```sh
python src/manage.py runserver
```

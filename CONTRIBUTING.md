# Contribution guidelines

## Development Environment Setup
If you wish to contribute to Leaktopus or run it in development mode, please follow this section. 

### Customized Docker compose for development
The dev version of docker-compose shares the volumes with the host machine for easy debugging and development.
```bash
docker-compose -f docker-compose.dev.yml -f docker-compose.override.yml up
```

### Without Docker (Manual)
#### Prerequisites
  - Python > 3.7
  - Pip
  - Node > 17.x
#### Backend
```bash
cd leaktopus_backend

# Required for using our .env file.
pip install python-dotenv

# Install all the dependencies.
pip install -r requirements.txt

# Run the application locally.
FLASK_APP="`pwd`/leaktopus/app.py" FLASK_DEBUG=1 flask run -p 8000

# To debug celery worker add these lines to the setting.py file.
import dotenv
dotenv.load_dotenv('./.env')
```

### Structure

The backend follows the Clean Architecture principles. Its structure is as follows:

* `leaktopus/domain` - Contains the domain use cases, interfaces (aka contracts), entities - the core of the business logic.
* `leaktopus/details` - Contains the implementations of the domain's interfaces, routing, asynchoronous tasks, and the database models.
* `leaktopus/services` - A glue between the domain and the details. Contains the services that are used by the domain use cases using the implementations from the details directory.
* `leaktopus/app.py` - The main application file. Contains the Flask app initialization and the routing.
* `leaktopus/factory.py` - The factory that creates the project services based on the settings in `settings.py`.

### Common Lanague

* `usecase` - A usecase is a single action that the user can perform. It usually includes a set of actions that are performed in a specific order. 
* `entrypoint` - Where we initial our details and execute a use case.
* `task` - A task is a background job that is executed asynchronously. E.g: a celery task, a thread.
* `service` - A glue between the domain's interfaces and the details' implementations. It is used by the use cases to execute the details' implementations.

#### Frontend
```bash
cd leaktopus_frontend

npm install
npm run serve
```
---

## Development/Monitoring Services
In addition to the services mentioned on the README.md file,
the following services can be used for development and advanced monitoring purposes:

| Service          | Port          | Documentation                                 |
| -------------    | ------------- | -------------                                 |
| Flower           | 5555          | https://flower.readthedocs.io/en/latest/      |
| Redis Commander  | 8081          | https://github.com/joeferner/redis-commander  |

_See docker-compose.override.example.yml for deployment examples._

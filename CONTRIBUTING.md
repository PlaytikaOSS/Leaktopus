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
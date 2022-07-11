<div align="center">

![](logos/logo-128.png)

# :sweat_drops:Leaktopus:octopus:

**Keep your source code under control.**

Based on the **Code C.A.I.N** framework:

:bird: **C**anarytokens

:mag_right: **A**utomated **I**nspection

:bomb: **N**eutralization

---

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![](https://img.shields.io/github/stars/Playtika/leaktopus?style=social)

</div>

---

## Key Features
  - **Plug&Play** - one line installation with Docker.
  - **Scan various sources** containing a set of keywords, e.g. `ORGANIZATION-NAME.com`.
    
    Currently supports:
    - GitHub
      - Repositories
      - Gists _(coming soon)_
    - Paste sites (e.g., PasteBin) _(coming soon)_
  - **Filter results** with a built-in heuristic engine.
  - **Enhance results with IOLs** (Indicators Of Leak):
      - Secrets in the found sources (including Git repos commits history):
        - With [Shhgit][1] (using a customized rules list).
        - With [TruffleHog][3].
      - URIs (Including indication of your organization's domains)
      - Emails (Including indication of your organization's email addresses)
      - Contributors
      - Sensitive keywords (e.g., canary token, internal domains)
  - Allows to **ignore** public sources, (e.g., "junk" repositories by web crawlers).
  - **OOTB ignore list** of common "junk" sources.
  - **Acknowledge a leak**, and only get notified if the source has been modified since the previous scan.
  - **Built-in ELK** to search for data in leaks (including full index of Git repositories with IOLs).
  - **Notify on new leaks**
    - MS Teams Webhook.
    - Cortex XSOAR® (by Palo Alto Networks) Integration _(Coming soon)_.

## Technology Stack
- Fully Dockerized.
- API-first Python Flask backend.
- Decoupled Vue.js (3.x) frontend.
- SQLite DB.
- Async tasks with Celery + Redis queues.

## Prerequisites
  - Docker-Compose

## Installation
  - Clone the repository
  - Create a local .env file
    ```bash
    cd Leaktopus
    cp .env.example .env
    ```
  - Edit .env according to your local setup (see the internal comments).
  - Run Leaktopus
    ```bash
    docker-compose up -d
    ```
  - Initiate the installation sequence by accessing the installation API.
    Just open http://{LEAKTOPUS_HOST}:8000/api/install in your browser.
  - Check that the API is up and running at http://{LEAKTOPUS_HOST}:8000/up
  - The UI should be available at http://{LEAKTOPUS_HOST}:8080


## Updating Leaktopus
If you wish to update your Leaktopus version (pulling a newer version), just follow the next steps.

  - Pull the latest version.
    ```bash
    git pull
    ```
  - Rebuild Docker images (data won't be deleted).
    ```bash
    # Force image recreation
    docker-compose up --force-recreate --build
    ```
  - Run the DB update by calling its API (should be required after some updates).
  http://{LEAKTOPUS_HOST}/api/updatedb

## Results Filtering Heuristic Engine
The built-in heuristic engine is filtering the search results to reduce false positives by:
- Content:
    - More than X emails containing non-organizational domains.
    - More than X URIs containing non-organizational domains.
- Metadata:
    - More than X stars.
    - More than X forks.
- Sources ignore list.

## API Documentation
OpenAPI documentation is available in http://{LEAKTOPUS_HOST}:8000/apidocs.

## Leaktopus Services
| Service          | Port          | Mandatory/Optional |
| -------------    | ------------- | -------------      |
| Backend (API)    | 8000          | Mandatory          |
| Backend (Worker) | N/A           | Mandatory          |
| Redis            | 6379          | Mandatory          |
| Frontend         | 8080          | Optional           |
| Elasticsearch    | 9200          | Optional           |
| Logstash         | 5000          | Optional           |
| Kibana           | 5601          | Optional           |

_The above can be customized by using a custom docker-compose.yml file._

## Security Notes
As for now, Leaktopus does not provide any authentication mechanism.
Make sure that you are not exposing it to the world, and doing your best to **restrict access to your Leaktopus instance(s)**.

## Contributing
Contributions are very welcomed.

Please follow our [contribution guidelines and documentation][2].

[1]: <https://github.com/eth0izzle/shhgit>
[2]: <https://github.com/Playtika/leaktopus/blob/main/CONTRIBUTING.md>
[3]: <https://github.com/trufflesecurity/trufflehog>

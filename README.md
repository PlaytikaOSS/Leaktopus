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
  - **Filter results** with a built-in heuristics engine.
  - **Enhance results with IOLs** (Indicators Of Leak):
      - Secrets
      - Domains _(highlight organizational domains)_
      - Emails _(highlight organizational email addresses)_
      - Contributors
      - Sensitive keywords (e.g., canary token, internal domains)
  - **Find secrets** in the found sources (including Git repos commits history):
    - With [Shhgit][1] (using a customized rules list).
    - With [TruffleHog][2].
  - Allows to **ignore** public sources, (e.g., "junk" repositories by web crawlers).
  - **OOTB ignore list** of common "junk" sources.
  - **Acknowledge a leak**, and only get notified if the source has been modified since the previous scan.
  - **Built-in ELK** to search for data in leaks (including full index of Git repositories that contains a "leak").
  - **Notify on new leaks**
    - MS Teams Webhook.
    - Cortex XSOAR® (by Palo Alto Networks) Integration _(Coming soon)_

## Technology Stack
- Fully Dockerized.
- API-first Python Flask backend.
- Decoupled Vue.js (3.x) frontend.
- SQLite DB.
- Async scans with Celery + Redis queues.

## Prerequisites
  - Docker-Compose

## Installation
  - Run Leaktopus
    ```bash
    docker-compose up -d
    ```
  - Initiate the installation sequence by accessing the installation API.
    Just open http://{LEAKTOPUS_HOST}:8000/api/install in your browser.
  - Check that the API is up and running at http://{LEAKTOPUS_HOST}:8000/up
  - The UI should be available at http://{LEAKTOPUS_HOST}:8080


## Updating Leaktopus
If you wish to upgrade your Leaktopus version, just follow the following steps.

  - Reinstall Leaktopus (data won't be deleted).
    ```bash
    # Force image recreation
    docker-compose up --force-recreate --build
    ```
  - Run the DB update by calling its API (should be required after some updates).
  http://{LEAKTOPUS_HOST}/api/updatedb

## Results Filtering Heuristic Engine
The built-in heuristic engine is filter the search results by:
- Content:
    - More than X emails containing other domains.
    - More than X domains containing other domains.
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
Contributions are mostly welcome.

Please follow our contribution guidelines and documentation. 
Contributions are very welcome! Please see our [contribution guidelines first][3].

[1]: <https://github.com/eth0izzle/shhgit>
[2]: <https://github.com/trufflesecurity/trufflehog>
[3]: <https://github.com/Playtika/leaktopus/blob/main/CONTRIBUTING.md>

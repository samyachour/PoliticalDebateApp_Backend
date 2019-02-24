## Political debate app (master)

This repo is the master for all our code repos. It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management and also indexes all our debate map documents.

### The app

The political debate app concept is simple: explore the pro & con sides of contentious issues via an interactive (bandersnatch-esque) interface.

#### Design

Each frontend homepage opens with a search bar, a grid of all our issues, and a login button in the top right (opens a modal with email & password, to register just adds a second confirm password field) ('log in' becomes a gear after login and leads to a settings page with log out, delete acct, and password/email change options).

![](Designs/Home.png)

Each point is accompanied by several responses (rebuttals). Some of these lead to separate points some lead deeper into this given point. At the end of a map the user just sees a darker 'complete button.'

![](Designs/Point.png)

#### Debate maps

The app's backend content can be modified by creating stylized text files called [debate maps](Debate_maps/Template) (usually with no extension).

The backend has a script that can parse these documents and create a new debate page based on it, with the frontends then pulling this on start.

#### Misc

- We use [Test-driven-development](https://en.wikipedia.org/wiki/Test-driven_development) to ensure minimal code debt.
- The intended user base is anyone who wants to solidify their arguments for a certain issue or explore the other side's perspective.

## Political debate app (backend)

This repo is the backend for each of the 3 frontend repos ([web](https://github.com/samyachour/PoliticalDebateApp_Web), [iOS](https://github.com/samyachour/PoliticalDebateApp_iOS), and [Android](https://github.com/samyachour/PoliticalDebateApp_Android)). It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management that is automatically managed by issues & pull requests.

### Framework

For our backend we use the [Django Rest Framework](https://www.django-rest-framework.org).

#### Usage

- Useful commands:
    - on start: `source venv/bin/activate` `pg_ctl -D /usr/local/var/postgres start` (or `stop`)
    - general: `python manage.py migrate` `psql PoliticalDebateApp`

#### Setup

- install latest python with homebrew `brew install python` or `brew upgrade python`
- run build_venv.sh `chmod +x build_venv.sh` `./build_venv.sh` to install and run your venv (needing python3.7 as well as django + djangorestframework)
- create a secrets.py file in PoliticalDebateApp/ with the secret key defined as the variable `secretKeyHidden` & PostgreSQL credentials `secretPostgreUser` and `secretPostgrePassword`

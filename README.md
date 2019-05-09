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

- We aggregate commits onto develop and merge onto master weekly incrementing version by release e.g. 'x.1' > 'x.2'
    - branches off develop must be associated with an existing issue and follow the naming convention 'issue[#]/[type]/[name]' for example 'issue7/enhancement/BasicDjangoRestSetup'
        - if necessary, we can create (& merge) hotfix branches off of master
    - submit pull requests to develop & attach a reviewer & associated issue (to automate kanban board task management)
- We use [Test-driven-development](https://en.wikipedia.org/wiki/Test-driven_development) to ensure minimal code debt.
- The intended user base is anyone who wants to solidify their arguments for a certain issue or explore the other side's perspective.

## Political debate app (backend)

This repo is the backend for each of the 3 frontend repos ([web](https://github.com/samyachour/PoliticalDebateApp_Web), [iOS](https://github.com/samyachour/PoliticalDebateApp_iOS), and [Android](https://github.com/samyachour/PoliticalDebateApp_Android)). It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management that is automatically managed by issues & pull requests.

### Framework

For our backend we use the [Django Rest Framework](https://www.django-rest-framework.org) with [PostgreSQL](https://www.postgresql.org).
- Django [models](https://docs.djangoproject.com/en/2.1/topics/db/models/), [form fields](https://docs.djangoproject.com/en/2.1/ref/forms/fields/), [model fields](https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.ManyToManyField), and [Postgres specific fields](https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#django.contrib.postgres.fields.ArrayField)
- Django rest [walkthrough](https://medium.com/backticks-tildes/lets-build-an-api-with-django-rest-framework-32fcf40231e5), [authentication](https://www.django-rest-framework.org/api-guide/authentication/), and [permissions](https://www.django-rest-framework.org/api-guide/permissions/)

#### Usage

- Useful commands:
    - on start: `source venv/bin/activate` `pg_ctl -D /usr/local/var/postgres start` (or `stop`)
    - django: `python manage.py makemigrations` `python manage.py migrate` `python manage.py test` `python manage.py runserver`
    - psql: `psql -d PoliticalDebateApp -U politicaldebateappowner` `\l` `\q` `\du` `drop database "(database)";` `create database "(database)";` `grant all privileges on database "(database)" to (user);` `create database postgres;`

#### Setup

Dependencies:
- Python 3.x (manual)
- [Django](https://www.djangoproject.com) 2.x
- [Django rest framework](https://www.django-rest-framework.org) 3.x
- [Django rest framework JWT](https://getblimp.github.io/django-rest-framework-jwt/) 1.x
- [PostgreSQL 11.x](https://www.postgresql.org) (manual)
- [Psycopg2](http://initd.org/psycopg/) 2.x

Instructions:
- install latest python with homebrew `brew install python` or `brew upgrade python`
- install latest postegresql with homebrew `brew install postgresql`
- run build_venv.sh `./build_venv.sh` to install and run your venv (needing python3.7 as well as django + djangorestframework)
- create a secrets.py file in PoliticalDebateApp/ with the variables `secretKeyHidden` (Django key) & `secretPostgreUser` and `secretPostgrePassword` (PostgreSQL credentials)

### Architecture

- Here are our current models:
    - User (default Django User model)
        - username: String
        - email: String
        - password: String
    - Token
    - Debate
        - title: String (unique)
        - last_updated: Date
        - debate_map: JSON Dict [String: Array[String]]
    - Progress
        - user: User (foreign key)
        - debate: Debate (foreign key)
        - completed: Bool
        - seen_points: Array[String (Debate.debate_map[point])]
    - Starred
        - user: User (foreign key)
        - starred_list: Debates (ManyToMany)


### Endpoints

- our current API version is v1, so all endpoints start with 'http://127.0.0.1:8000/api/v1/'
- use `%20` for spaces
- when you see numbers associated with model types (e.g. `debate: 1`) the number is the ID (unique primary key (`pk`))

#### `auth/register/`

- register new user with credentials

POST

- Takes:

```
Body
{
    "email": "test@mail.com",
    "username": "test_username",
    "password": "test_password"
}
```

- Returns:

`HTTP_201_CREATED` or `HTTP_400_BAD_REQUEST` (with error message)


#### `auth/login/`

- login user to get token for session

POST

- Takes:

```
Body
{
    "username": "test_username",
    "password": "test_password"
}
```

- Returns:

```
{
    "token": (JSON Web Token)
}
```
or `HTTP_401_UNAUTHORIZED`

#### `auth/refresh-token/`

- need to keep checking if token is almost expired, if so ask for a refresh
- access token expires every 10 minutes
- refresh window is up to 30 days

POST

- Takes:

```
Body
{
    "token": (existing JSON web token)
}
```

- Returns:

```
{
    "token": (new JSON Web Token)
}
```
or
`HTTP_400_BAD_REQUEST` (with error message)

#### `auth/change-password/`

- change user password

POST

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```
```
Body
{
    "old_password": "test_old_password",
    "new_password": "test_new_password"
}
```

- Returns:

`HTTP_200_OK` or `HTTP_401_UNAUTHORIZED`

#### `debate/<int:pk>`

- get a debate by primary key
- load entire map into memory and use to present map flow to users marking points as seen as you go

GET

- Returns:

```
{
    "pk": 1,
    "title": "test_debate_pro",
    "last_updated": "2019-03-17",
    "debate_map": {
        "main - point1": {
            "description": "main point1 description",
            "non-sequitur rebuttal": "main point1 formatted as non-sequitur rebuttal",
            "styling": { "references": ["research.com/article1", "research.com/article2"], "images": ["image1 url", "image2 url"] },
            "secondary - point1": {
                "description": "secondary point1 description",
                "non-sequitur rebuttal": "secondary point1 formatted as non-sequitur rebuttal",
                "styling": {""},
                "secondary - point1": {""}
            },
            "secondary - point2": {""}
        },
        "main - point2": {""}
    }

}
```
or `HTTP_404_NOT_FOUND`

#### `debates/`

- get all debates
- will only ever return a maximum of 100 debates (50 w/ pro & con combined)
- should be 2 debates for every topic postfixed with either a `_pro` or a `_con`

GET

- Returns:

```
[
    {
        "pk": 1,
        "title": "test_debate_pro",
        "last_updated": "2019-03-17",
        "debate_map": {
            "main - point1": {
                "description": "main point1 description",
                "non-sequitur rebuttal": "main point1 formatted as non-sequitur rebuttal",
                "styling": { "references": ["research.com/article1", "research.com/article2"], "images": ["image1 url", "image2 url"] },
                "secondary - point1": {
                    "description": "secondary point1 description",
                    "non-sequitur rebuttal": "secondary point1 formatted as non-sequitur rebuttal",
                    "styling": {""},
                    "secondary - point1": {""}
                },
                "secondary - point2": {""}
            },
            "main - point2": {""}
        }

    },
    {
        "pk": 2,
        "title": "test_debate_con",
        "last_updated": "2019-03-17",
        "debate_map": {
        	"main - point1": {
                "description": "main point1 description",
                "non-sequitur rebuttal": "main point1 formatted as non-sequitur rebuttal",
                "styling": { "references": ["research.com/article1", "research.com/article2"], "images": ["image1 url", "image2 url"] },
        		"secondary - point1": { 
                    "description": "secondary point1 description",
                    "non-sequitur rebuttal": "secondary point1 formatted as non-sequitur rebuttal",
                    "styling": {""},
                    "secondary - point1": {""}
                },
                "secondary - point2": {""}
            },
            "main - point2": {""}
        }
    }
]
```

#### `progress/<int:pk>`

- get user's seen points for given debate

GET

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```

- Returns:

```
{
    "debate": 1,
    "completed": False,
    "seen_points": [
        "main - test_point", "secondary - test_point", "secondary - test_point"...
    ]
}
```
or `HTTP_404_NOT_FOUND`, `HTTP_400_BAD_REQUEST`

#### `progress/`

- get all debates user has made progress on

GET

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```

- Returns:

```
[
    {
        "debate": 1,
        "completed": False,
        "seen_points": [
            "main - test_point", "secondary - test_point", "secondary - test_point"...
        ]
    }
]
```

#### `progress/`

- add new seen point to user's debate progress

POST

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```
```
Body
{
    "debate_pk": 1,
    "debate_point": "point"
}
```

- Returns:

```
{
    "debate": 1,
    "completed": False,
    "seen_points": [
        "main - test_point", "secondary - test_point", "secondary - test_point"...
    ]
}
```
or `HTTP_400_BAD_REQUEST`

#### `progress-completed/`

- set progress completion status for a user's debate

POST

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```
```
Body
{
    "debate_pk": 1,
    "completed": True
}
```

- Returns:

```
{
    "debate": 1,
    "completed": True,
    "seen_points": [
        "main - test_point", "secondary - test_point", "secondary - test_point"...
    ]
}
```
or `HTTP_400_BAD_REQUEST`

#### `starred-list/`

- get all debates user has starred

GET

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```

- Returns:

```
{
    "starred_list": [
        1, 2, 3...
    ]
}
```
or `HTTP_404_NOT_FOUND`

#### `starred_list/`

- add new debate to user's starred list

POST

- Takes:

```
Header
{
    "Authorization": (JSON Web Token)
}
```
```
Body
{
    "debate_pk": 1
}
```

- Returns:

```
{
    "starred_list": [
        1, 2, 3... (debate (unique) IDs)
    ]
}
```
or `HTTP_400_BAD_REQUEST`

## Political debate app (master)

This repo is the master for all our code repos. It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management.

### The app

The political debate app concept is simple: explore the full debate map of a given issue via an interactive (bandersnatch-esque) interface.

#### Design

Each frontend homepage opens with a search bar, a grid of all our issues, and a login button in the top right (opens a modal with email & password, to register just adds a second confirm password field) ('log in' becomes a gear after login and leads to a settings page with log out, delete acct, and password/email change options).

![](Designs/Home.png)

Each point is accompanied by several responses (rebuttals). Some of these lead to separate points some lead deeper into this given point. At the end of a map the user just sees a darker 'complete button.'

![](Designs/Point.png)

#### Debate maps

The app's backend content can be modified by creating JSON files called [debate maps](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/DebateSingle.json).

The backend feeds these to the clients who know how to navigate & display these maps (need to handle logic locally in case user is not logged in (or potentially offline), will have to store progress anyway).

#### Misc

- We aggregate commits onto develop and merge onto master weekly incrementing version by release e.g. 'x.1' > 'x.2'
    - branches off develop must be associated with an existing issue and follow the naming convention 'issue[#]/[type]/[name]' for example 'issue7/enhancement/BasicDjangoRestSetup'
        - if necessary, we can create (& merge) hotfix branches off of master
    - submit pull requests to develop & attach a reviewer & associated issue (to automate kanban board task management)
- We use [test-driven-development](https://en.wikipedia.org/wiki/Test-driven_development) to ensure minimal code debt.
- The intended user base is anyone who wants to solidify their arguments for a certain issue or explore the other side's perspective.

## Political debate app (backend)

This repo is the backend for each of the 3 frontend repos ([web](https://github.com/samyachour/PoliticalDebateApp_Web), [iOS](https://github.com/samyachour/PoliticalDebateApp_iOS), and [Android](https://github.com/samyachour/PoliticalDebateApp_Android)). It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management that is automatically managed by issues & pull requests.

### Framework

For our backend we use the [Django Rest Framework](https://www.django-rest-framework.org) with [PostgreSQL](https://www.postgresql.org).
- Django [models](https://docs.djangoproject.com/en/2.1/topics/db/models/), [form fields](https://docs.djangoproject.com/en/2.1/ref/forms/fields/), [model fields](https://docs.djangoproject.com/en/2.1/ref/models/fields/#django.db.models.ManyToManyField), and [Postgres specific fields](https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#django.contrib.postgres.fields.ArrayField)
- Django rest [walkthrough](https://medium.com/backticks-tildes/lets-build-an-api-with-django-rest-framework-32fcf40231e5), [authentication](https://www.django-rest-framework.org/api-guide/authentication/), and [permissions](https://www.django-rest-framework.org/api-guide/permissions/)

#### Setup

Dependencies:
- Python 3.x (manual)
- [Django](https://www.djangoproject.com) 2.x
- [Django rest framework](https://www.django-rest-framework.org) 3.x
- [Django rest framework SimpleJWT](https://github.com/davesque/django-rest-framework-simplejwt) 3.x
- [PostgreSQL 11.x](https://www.postgresql.org) (manual)
    - [Trigram Similarity](https://www.postgresql.org/docs/current/pgtrgm.html)
- [Psycopg2](http://initd.org/psycopg/) 2.x

Instructions:
- install latest python with homebrew `brew install python` or `brew upgrade python`
- install latest postegresql with homebrew `brew install postgresql`
- run build_venv.sh `./build_venv.sh` to install and run your venv (needing python3.7 as well as django + djangorestframework)
- create a secrets.py file in PoliticalDebateApp/ with the constants `secretKeyHidden` (Django key) & `secretPostgreUser` and `secretPostgrePassword` (PostgreSQL credentials)

### Architecture

- Here are our current models:
    - Debate
        - title: String (unique)
        - short_title: String
        - tags: String (optional)
        - last_updated: Date
        - total_points: Int
        - debate_map: JSON Dict [String: Array[String]]
    - Point
        - debate: Debate (foreign key) (optional)
        - rebuttals: Points (ManyToMany) (optional)
    - PointImage
        - point: Point (foreign key)
        - url: URL
        - source: String
        - name: String (optional)
    - PointHyperlink
        - point: Point (foreign key)
        - substring: String
        - url: URL
    - Progress
        - user: User (foreign key)
        - debate: Debate (foreign key)
        - completed_percentage: Int
        - seen_points: Points (ManyToMany)
    - Starred
        - user: User (foreign key)
        - starred_list: Debates (ManyToMany)
    - User (default Django User model)
        - username: String
        - email: String
        - password: String
    - Token

### Endpoints

- our current API version is v1, so all endpoints start with 'http://127.0.0.1:8000/api/v1/'
- use `%20` for spaces
- all endpoints are [throttled](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/PoliticalDebateApp/settings.py#L77), so retries should only be done for error codes 408, 502, 503 and 504 (and technically 401 but you would need to refresh your access token first)
- all endpoint responses are available as [stubbed JSON files](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses) for clients to use as mocked responses in local unit testing.

---
#### DEBATES

##### `debate/<int:pk>`

- get a debate by primary key
- load entire map into memory and use to present map flow to users marking points as seen as you go

GET

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/DebateSingle.json)) or `404`

##### `debate/filter/`

- the debate maps do not come in this call
- all responses are sorted by most recent per the last updated property, therefore all parameters are **optional**
- response array limit is 100 debates, e.g.:
    - if a user has starred more than 100 debates they will get the most recently updated 100
    - if a user filters by random it will randomize the 100 most recently updated debates

###### Search string parameter
- searches debate database with the given string as a query comparing to the title and tags fields
- supports fuzzy string comparison

###### Filter parameters
- Filters:
    - `last_updated` (default)
    - `starred` (requires starred array)
    - `progress` (requires progress array)
    - `no_progress` (requires progress array)
    - `random`
- must pass in progress or starred arrays even if you are authenticated because this endpoint is also open to unauthenticated clients (who pass in local data), simpler to have just one
- must do progress ascending/descending sorting locally on the client

POST

- Takes:

```
Body
{
    "search_string": "gun",
    "filter": "progress",
    "all_progress": [2, 8, 4], # primary keys of debates user has made progress on
    "all_starred": [1, 2, 31] # primary keys of debates user has starred
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/DebateFilter.json)) or `404`

---
#### PROGRESS

##### `progress/<int:pk>`

- get user's seen points for given debate

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/ProgressSingle.json)), `404`, or `400`

##### `progress/`

- get all debates user has made progress on
- the seen points do not come in this call

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/ProgressAll.json))

##### `progress/`

- add new seen point to user's debate progress

POST

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```
```
Body
{
    "debate_pk": 1,
    "point_pk": 1
}
```

- Returns:

`201`, `401`, `404`, or `400`

##### `progress/batch/`

- add an array of debates' seen points' IDs to user's progress

POST

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```
```
Body
{
    "all_debate_points": [
        {
            "debate": 1,
            "seen_points": [
                1, 2, 3, 4...
            ]
        },
        {
            "debate": 2,
            "seen_points": [
                1, 2, 3, 4...
            ]
        }
    ]
}
```

- Returns:

`201`, `401`, or `400`

---
#### STARRED

##### `starred/`

- get all debates user has starred

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/Starred.json))

##### `starred/`

- update user's starred debates
- can sync local data w/ backend in one call

POST

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```
```
Body
{
    "starred_list": [1, 2, 3, 4],
    "unstarred_list": [5, 6]
}
```

- Returns:

`201` or `401`

---
#### AUTH

##### `auth/register/`

- register new user with credentials
- verification email is automatically sent to user's email, clients should express this

POST

- Takes:

```
Body
{
    "email": "test@mail.com",
    "password": "test_password"
}
```

- Returns:

`201` or `400`

##### `auth/request-password-reset/`

- request link to reset user password
- reset link is automatically sent to user's email, clients should express this
- force_send is if the user hasn't confirmed their email, they can force send the reset link anyway

POST

- Takes:

```
Body
{
    "email": "test@mail.com",
    (optional, defaults to false) "force_send": true
}
```

- Returns:

`201`, `400`, or `404`

##### `auth/token/obtain/`

- login user to get token for session
- use the "username" key but pass in the user's email
- username needs to be lowercase
- save refresh and access tokens to secure persistent data

POST

- Takes:

```
Body
{
    "username": "test@mail.com",
    "password": "test_password"
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/TokenObtain.json)) or `400`

##### `auth/token/refresh/`

- when you get a 401, refresh your access token
- access token expires every 10 minutes
- refresh window is up to 30 days

POST

- Takes:

```
Body
{
    "refresh": (existing JSON Web Refresh token)
}
```

- Returns:

`200` ([See file here](https://github.com/samyachour/PoliticalDebateApp_Backend/blob/develop/StubbedResponses/TokenRefresh.json)) or `400`

##### `auth/change-password/`

- change user password

PUT

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
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

`200`, `401`, or `400`

##### `auth/change-email/`

- change user email
- verification email is automatically sent to user's email, clients should express this

PUT

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```
```
Body
{
    "new_email": "test@mail.com"
}
```

- Returns:

`200`, `401`, or `400`

##### `auth/delete/`

- delete user account & all associated data

POST

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` or `401`

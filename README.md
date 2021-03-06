## Political debate app (backend)

This repo is the backend for each of the 3 frontend repos ([web](https://github.com/samyachour/PoliticalDebateApp_Web), [iOS](https://github.com/samyachour/PoliticalDebateApp_iOS), and [Android](https://github.com/samyachour/PoliticalDebateApp_Android)). It has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management that is automatically managed by issues & pull requests.

#### Setup

Dependencies
- [see file here](requirements.txt)

Instructions:
- install latest python with homebrew `brew install python` or `brew upgrade python`
- install latest postegresql with homebrew `brew install postgresql`
- run build_venv.sh `./build_venv.sh` to install and run your venv
- run `./reset_database.sh` to create local database
- request a `set_env.sh` w/ all necessary env variables

### Architecture

- Here are our current models:
    - Debate
        - title: String (unique)
        - short_title: String
        - tags: String (optional)
        - last_updated: DateTime
        - total_points: Int
        - all_points_primary_keys: [Int]
    - Point
        - debate: Debate (foreign key) (optional)
        - description: String (primary key part 1)
        - short_description: String (primary key part 2)
        - side: String ("lib", "con", or "context")
        - rebuttals: Points (ManyToMany) (optional)
        - time_added: DateTime
    - PointHyperlink
        - point: Point (foreign key)
        - substring: String
        - url: URL
    - Progress
        - user: User (foreign key)
        - debate: Debate (foreign key)
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

- debug URL: `https://politicaldebateapp-debug.herokuapp.com/api/`
    - endpoint throttling is turned off
    - has hundreds of dummy debates and test accounts
    - produces verbose logs on the backend
    - emails don't really send, they just get logged
- production URL: `https://politicaldebateapp-prod.herokuapp.com/api/`
- our current API version is v1, so all endpoints start with `v1/`
- all endpoints are [throttled](PoliticalDebateApp/settings.py#L77)
- all endpoint responses are available as [stubbed JSON files](stubbed_responses) for clients to use as mocked responses in local unit testing.

---
#### DEBATES

##### `debate/<int:pk>`

- get a debate by primary key

GET

- Returns:

`200` ([See file here](stubbed_responses/DebateSingle.json)) or `404`

##### `debate/filter/`

- all responses are sorted by most recent per the last updated property, therefore all parameters are **optional**
- the `debate_map` & `all_points_primary_keys` properties do not come in this call
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

`200` ([See file here](stubbed_responses/DebateFilter.json)) or `404`

---
#### PROGRESS

##### `progress/`

- get all debates user has made progress on

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` ([See file here](stubbed_responses/ProgressAll.json))

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

`201` or `401`

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

`200` ([See file here](stubbed_responses/Starred.json))

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

`200`, `400`, or `404`

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

`200` ([See file here](stubbed_responses/TokenObtain.json)), `400`, `401`, or `404`

##### `auth/token/refresh/`

- when you get a 401, refresh your access token
- in prod, access tokens expire after a week and refresh after a year
- in debug, access tokens expire after 3 minutes and refresh after a week

POST

- Takes:

```
Body
{
    "refresh": (existing JSON Web Refresh token)
}
```

- Returns:

`200` ([See file here](stubbed_responses/TokenRefresh.json)) or `400`

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

##### `auth/get-current-email/`

- get the user's current email address and whether or not it's verified

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200` ([See file here](stubbed_responses/GetCurrentEmail.json)) or `401`

##### `auth/request-verification-link/`

- send a verification link to the user's unverified email address

GET

- Takes:

```
Header
{
    (Bearer token): (JSON Web Access Token)
}
```

- Returns:

`200`, `400`, or `401`

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

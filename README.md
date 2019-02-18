## Political debate app (master)

This repo is the master for all our code repos.

This repo has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management. It also indexes all our debate map documents.

### The App

The political debate app concept is simple: explore the pro & con sides of contentious issues via an interactive (bandersnatch-esque) interface.

#### Design

Each frontend homepage opens with a search bar, a grid of all our issues, and a login button in the top right.

#### Debate maps

The app's backend content can be modified by creating stylized text files called [debate maps](Debate_maps/Template) (usually with no extension).

The backend has a script that can parse these documents and create a new debate page based on it, with the frontends then pulling this on start.

#### Misc

- The intended user base is anyone who wants to solidify their arguments for a certain issue or explore the other side's perspective.

## Political debate app (backend)

This repo is the backend for each of the 3 frontend repos ([web](https://github.com/samyachour/PoliticalDebateApp_Web), [iOS](https://github.com/samyachour/PoliticalDebateApp_iOS), and [Android](https://github.com/samyachour/PoliticalDebateApp_Android)).

Each repo has a [kanban board](https://github.com/samyachour/PoliticalDebateApp_Backend/projects/1?fullscreen=true) for task management that is automatically managed by issues & pull requests.

## Framework

For our backend we use a Django REST-API.

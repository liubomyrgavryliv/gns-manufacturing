# gns-manufacturing

This is an internal web application developed specifically for [Gavryliv&Sons company](https://gavrylivsons.com.ua/en/) for tracking the work progress and assigning tasks for the employees.

Before start working with the project **make sure** you have next things installed on your system:

- [Git](https://github.com/git-guides/install-git)

- [Docker](https://docs.docker.com/get-docker/)

- [Docker-compose](https://docs.docker.com/compose/install/)

- [Make](https://www.gnu.org/software/make/) 


In order to make the database running on your machine do the following:

1. Clone the project into your local environment using command `git clone git@github.com:liubomyrgavryliv/gns-manufacturing.git`
2. Rename `.env.sample` to `.env`.
3. Call commands to start the db and initialize the db structure by running `make init-db`. Your local database is now running locally from the *docker container* in the background and you can connect to it through any database environment tool by using these arguments (from `.env.sample`):<br>
    - host=localhost
    - port=3306
    - database=gns
    - username=gns
    - password=gns

When stop working with the database shutdown the docker container by running this command `make stop-db`.
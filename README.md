# ZSSN

A repository for the coding test of Infog2

## API documentation

The documentation of the API is on the following link https://documenter.getpostman.com/view/19053288/UVXesdk8

# Tutorial

## Docker
This project uses Docker, you'll need to install Docker to properly run the API, in case you don't have Docker installed, you can download it in this website: https://docs.docker.com/get-docker/

## .env
Before executing the API, you'll need to set the .env file. Firstly, rename the ".env.sample" file to ".env". Then, insert values into the variables of the .env file. The variables are detailed bellow:

1. DEBUG: True or False;
2. SECRET_KEY: A Django secret key, which you can generate in this website: https://djecrety.ir/
3. DB_NAME: The name of your postgres database.
4. DB_USER: The username of your postgres database.
5. DB_PASS: The password of your postgres database.
6. DB_HOST: The host of your postgres database.
  - This should have the same name as the postgres service in the docker-compose file, if you don't want to change the service's name just give this variable the value of "db".
7. DB_PORT: The port of your postgres database.
8. PTS_WATER= Amount of points the water is worth
9. PTS_FOOD= Amount of points the food is worth
10. PTS_MEDS= Amount of points the meds is worth
11. PTS_AMMO=  Amount of points the ammo is worth
  
## Execute the API
 
Before executing the api, you'll need to start the docker program, and then use the following commands on the root directory of this project:

``` docker-compose build ```

This command will download the images and build the services required to run the API. After that you'll just need to use this command:

``` docker-compose up ```

And then the API will work properly.

## Testing

You can run the automated tests using the following command:

```  docker-compose run web python manage.py test  ```

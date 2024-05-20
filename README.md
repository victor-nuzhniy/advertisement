# advertisement

## Description

1. Project created for aggregate advertisements.
2. Every day in defined time advertisements created earlier than 24 hours
   ago will be deleted.
3. Every day in defined time given platform will be scrapped for the advertisements.
4. Gathered info:
    - url
    - price in $
    - car name
    - model
    - region
    - run
    - color
    - salon
    - contacts
5. Only admin user can access admin interface.
6. Only authorized user can access endpoints with aggregated info.
7. There is endpoint with info filtered for time period.
8. There is endpoint with statistic info concerning minimal, maximal prices,
    advertisements number per day, week, month for particular car name and model.
9. Swagger api can be accessed by http://127.0.0.1:8000/docs#/

## Sensitive data

Create in the project root .env file with sensitive info. It should contain possible keys
and values:
POSTGRES_HOST=postgres_adv
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=advertisement

REDIS_HOST=redis
REDIS_PORT=6379

DB_ADMIN_USERNAME=alex
DB_ADMIN_EMAIL=a@a.com
DB_ADMIN_PASSWORD=1111

SCRAP_TIMEOUT = 5
CLEAN_TIME_HOUR = 6
CLEAN_TIME_MINUTE = 1
SCRAP_TIME_HOUR = 7
SCRAP_TIME_MINUTE = 1

DEBUG = 1

All possible settings that can be set to the project, can be found in settings.py in root.
DB_ADMIN username, email, password are needed for creating admin user.
SCRAP_TIMEOUT - seconds to sleep between accessing platform for preventing to be banned.
In DEBUG mode scrapper is limited to load only 2 pages collecting advertisements
pages url, and to load only 10 pages from saved list.

## Project installation steps with docker locally

1. Clone project
2. Create .env file with info described earlier.
3. Run docker-compose up.
4. Try app with domain http://127.0.0.1:8000/docs#/
5. For forced loading scraped data SCRAP_TIME_HOUR and SCRAP_TIME_MINUTE can
    be set right after the current time.

   
## Testing

1. To perform testing at least db container should run. And
   .env POSTGRES_HOST=localhost, POSTGRES_PORT=8778 should be set.
2. Test dependencies should be installed with       poetry install --with test
2. To run test perform command    pytest --cov
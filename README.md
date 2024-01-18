# MOOD TRACKER API
### Tracks various lifestryle routines to better evaluate your mood

This is the API project for the Mood Tracker app, used to track mood, water intake, exercises and food habits to better map your mood throughout the days.

## Requirements

In order to run this API you will need:

1. [Python](https://www.python.org/downloads/) 3.11
2. [PostgreSQL](https://www.postgresql.org/download/) 15
3. [Poetry](https://python-poetry.org/docs/#installation)
4. Configure env files:
   1. `.env`
   2. `.secrets.toml`

Install all dependencies running poetry install command:
> \> poetry install

## The API

This API was built using [Falcon Web Framework](https://falcon.readthedocs.io/en/stable/). There are 5 Resources: `Humor` for humor, `Exercises` for exercises, `Water` for water intake, `Food` for food habits, and `Mood` for the combination of all.

These are the three main endpoints:

1. `/<resource>`
2. `/<resource>/{resource_id: int}`
3. `/<resource>/date/{YYYY-MM-DD}`

Endpoint `1` is for adding a new resource with `HTTP POST`. The data for the resource should be in the body of your request, and each resource has their own specific data.

For all cases, `date` is an optional argument, that defaults to `today` if left out.

- Exercises:
  - `minutes`: how long was the exercise session.
  - `description`: what was done in this session.
- Food:
  - `value`: an evaluation for this food habit.
  - `description`: a description of what you're eating, or an explanation on why you gave such evaluation.
- Water:
  - `milliliters`: how much water, in ml, you've consumed.
  - `description`: an explanation for the amount you've consumed.
  - `pee`: a boolean (true/false) if you had excessive peeing.
- Humor:
  - `value`: an evaluation for your current humor.
  - `description`: an explanation on why you gave such evaluation.
  - `health_based`: a boolean (true/false) if your health influenced your evaluation.
- Mood:
  - `humor`: a Humor object
  - `water_intake`: a Water object.
  - `exercises`: an Exercises object.
  - `food_habits`: a Food object.

Endpoint `2` is for actions targeted to a specific Resource. They are `HTTP GET`, `HTTP PATCH` and `HTTP DELETE`. For all of them, you have to pass the `resource_id`. For example, if you want to get the data from Exercises #314, your endpoint should look like this:
> /exercises/314

Endpoint `3` is for actions that target multiple resources at once. They are `HTTP GET` and `HTTP DELETE`. They will return and delete, respectively, all entries of the Resource in the database for the date passed.

## Tests

All tests were built using [Pytest Framework](https://docs.pytest.org/en/7.4.x/).
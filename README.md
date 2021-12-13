# Team Hippopotamus Small Group project

## Team members
The members of the team are:
- Mikolaj Deja
- Yasath Dias
- Amman Kiani
- Zafira Shah
- Brendon Zoto

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [this Heroku link](https://warm-cove-08022.herokuapp.com).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`. In addition:
- The animated background used on the Welcome screen is sourced from [VantaJS](https://www.vantajs.com/?effect=net),
- The daily Chess puzzle on the homepage is from [ChessPuzzle.net](https://chesspuzzle.net/Daily),
- The pie charts on user profile pages are made using [Chart.js](https://www.chartjs.org),
- The sortable data tables are made using [Simple-DataTables](https://github.com/fiduswriter/Simple-DataTables),
- The [chess pieces glyph](https://fontawesome.com/v5.15/icons/chess?style=solid) by the navbar logo, and the [quotation mark glyph](https://fontawesome.com/v5.15/icons/quote-left?style=solid) by the homepage pun, are from [FontAwesome](https://fontawesome.com/),
- The font used is `IBM Plex Sans` sourced from [Google Fonts](https://fonts.google.com/specimen/IBM+Plex+Sans).
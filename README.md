# Kazan road city graph

![](https://images-for-something.s3.us-east-2.amazonaws.com/2.+%D0%94%D0%B5%D1%80%D0%B5%D0%B2%D0%BE+%D0%BA%D1%80%D0%B0%D1%82%D1%87.+%D0%BF%D1%83%D1%82%D0%B5%D0%B8%CC%86.png | width=900)

<img src="https://images-for-something.s3.us-east-2.amazonaws.com/2.+%D0%94%D0%B5%D1%80%D0%B5%D0%B2%D0%BE+%D0%BA%D1%80%D0%B0%D1%82%D1%87.+%D0%BF%D1%83%D1%82%D0%B5%D0%B8%CC%86.png" width="900" height="300" />

# Frontend

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Usage
All frontend files are in folder "city-graph". Make sure you had already installed needed dependencies (by running: yarn install). Also make sure you had started the backend server to receive requests from frontend. To run the project you need to run a command below:

### `yarn start`

After you would have to generate some number of nodes upon which algorithms would do their stuff (step 1 in a picture below) and after press the button "Сгенерировать на карте"(step 2) for the actual generation to take place.
![](https://images-for-something.s3.us-east-2.amazonaws.com/templ.png)

Then run any algorithm on these generated nodes by pressing the corresponding buttons below

## Available Scripts

In the project directory, you can run:

### `yarn install`

Installs all necessary dependencies

### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).


# Backend

## Usage

All backend files are in folder "city-graph-backend". Make sure you had already installed all necessary packages (by running: pip install -r requirements.txt). To run the backend server you would need to run the command:

### `python3 app.py`

## Installation

Install necessary dependencies with pip:

### `pip install -r requirements.txt`

## Flask Configuration

#### Example

```
app = Flask(__name__)
app.config['DEBUG'] = True
```
### Configuring From Files

#### Example Usage

```
app = Flask(__name__ )
app.config.from_pyfile('config.Development.cfg')
```

## Run Flask
### Run flask for develop
```
$ python webapp/run.py
```
In flask, Default port is `5000`

Swagger document page:  `http://127.0.0.1:5000/api`

### Run flask for production

** Run with gunicorn **

In  webapp/

```
$ gunicorn -w 4 -b 127.0.0.1:5000 run:app

```

* -w : number of worker
* -b : Socket to bind


### Run with Docker

```
$ docker build -t flask-example .

$ docker run -p 5000:5000 --name flask-example flask-example 
 
```

In image building, the webapp folder will also add into the image


## Unittest
```
$ nosetests webapp/ --with-cov --cover-html --cover-package=app
```
- --with-cov : test with coverage
- --cover-html: coverage report in html format

## Reference

Offical Website

- [Flask](http://flask.pocoo.org/)

Tutorial

- [Flask Overview](https://www.slideshare.net/maxcnunes1/flask-python-16299282)
- [In Flask we trust](http://igordavydenko.com/talks/ua-pycon-2012.pdf)

# Contributors
#### - [Laistseva Milena](https://github.com/MilRoad) Algorhtms
#### - [Orlov Kirill](https://github.com/orlodox) Algorithms
#### - [Samedov Nihad](https://github.com/orlodox) Frontend, Backend

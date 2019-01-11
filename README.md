# wod-stats

A simple Django app that fetches any Workout of the Day ("WOD") from the crossfit.com website, parses the comments and categorizes them based on gender and workout completion (i.e. as prescribed "Rx" or scaled).

This app produces simple statistics that inform users on how to scale the difficulty and how to improve. 

For example, a person trying to complete the WOD as prescribed ("Rx") can 

1. see the ratio of Rx versus all comments and 
2. filter comments to see the demographics of those completed and their results.

That informs the user on whether to attempt to Rx, scale the difficulty, substitute movements, etc. in order to get a better workout and set targets that help them improve over time.

# How to Run

Setup a virtual environment

`virtualenv venv-fitjstats`

Clone the repo

`git clone https://github.com/laukevinh/wod-stats.git`

Activate the virtual env (assuming you setup the virtualenv in your home dir).

`source ~/venv-fitjstats/bin/activate`

Don't forget to install all requirements.

```
cd ~/wod-stats/
pip install -r requirements.txt
```

Go to your project folder and run the server

```
cd ~/wod-stats/
python manage.py runserver
```



# Future features

- Add age, weight and height to filter. Current challenge is that most users share that information in the comment, but they do not share it in a standard format.
- Analyze workout results (e.g. time, reps, weight) and display simple statistics (e.g. best, avg, worst) based on filters.

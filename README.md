# wod-stats

A simple Django app that fetches any Workout of the Day ("WOD") from the crossfit.com website, parses the comments and categorizes them based on gender and workout completion (i.e. as prescribed "Rx" or scaled).

This app produces simple statistics that inform users on how to scale the difficulty and how to improve. 

For example, a person trying to complete the WOD as prescribed ("Rx") can 

1. see the ratio of Rx versus all comments and 
2. filter comments to see the demographics of those completed and their results.

That informs the user on whether to attempt to Rx, scale the difficulty, substitute movements, etc. in order to get a better workout and set targets that help them improve over time.

# Future features

- Add age, weight and height to filter. Current challenge is that most users share that information in the comment, but they do not share it in a standard format.
- Analyze workout results (e.g. time, reps, weight) and display simple statistics (e.g. best, avg, worst) based on filters.

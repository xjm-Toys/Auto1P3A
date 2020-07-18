# auto1point3Acres

## Summary

An automated script to get the daily reward in 1point3auto (一亩三分地), utilizing pytesseract to crack the captcha, deployed on Heroku

## Deployment

### Step1: create your Heroku app

Click the `Deploy to Heroku` Button below, this will take you to a website that helps you set up an Heroku app, (you need to create an account first if you don't have one)

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Step2: set up variables

Input the `USERNAME` and `PASSWORD` values with your 1point3acres username and password.

<img src="https://i.imgur.com/jV8a7fQ.png" width="600px">

### Step3: deploy and build

Hit **Deploy App** and wait until the build is finished. Click `Manage App` redirects to the main page.

<img src="https://i.imgur.com/UnHlu8Q.png" width="600px">

### Step4: set up schedules

- Click `Resources` > `Heroku Scheduler` > `Create Job`
- Choose `Every day at ...` with anytime you like
- Copy and paste `python main.py` in the command input below
- Save job

<img src="https://i.imgur.com/hj6adwI.png">

### All set

Now your Heroku app will follow the schedule you just set and execute the script that gets all daily reward!

## Manually run the script(optional)

### First way: using Heroku console

1. Go to your Heroku app page. (Can be accessed if you log in to your Heroku account).
2. At top right of the page, click `More` > `Run console`.
3. Now you should have console opened, input `bash` and click `Run`.
4. Wait until the console logged, then run the command `python main.py`.

### Second way: run the Heroku app locally

**NOTE**: Before using any command, make sure you have installed and login to Heroku, the instruction can be found in [install Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

```code
Heroku login
Heroku run main --app <YOUR_APP_NAME>
```

## Credit

- [1p3a_python_script](https://github.com/VividLau/1p3a_python_script)

The code is forked from this project, which automated the process of login to 1point3acres and gets the daily reward. One thing to point out is that it uses `pytesseract` for authentication code recognition, which makes it fully automated.

- [1point3auto](https://github.com/CryoliteZ/1point3auto)

I followed this project's idea and instructions to deploy the script to Heroku, which simplified the deployment to almost one click.

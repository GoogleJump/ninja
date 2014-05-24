This code allows a user to insert a moment on to their Google + profile.

1. Install the App Engine Python SDK: https://developers.google.com/appengine/downloads

2. Within the project directory, install dependencies to the lib directory:
	
	```
	$ pip install -r requirements.txt -t lib
	```

3. Run this project locally from the command line:

	```
	dev_appserver.py .
	```

4. Navigate to http://localhost:8080/

5. Sign in with a Google+ account

6. Click to insert a "moment" on to your profile

7. To view the moment:
	- Go to the "About" tab of your Google+ profile.
	- Scroll down to "Apps with Google+ Sign-in"
	- Click "Bouncehouse"

8. To push code to Google App Engine

	```
	appcfg.py --version=${dev_name} update .
	```
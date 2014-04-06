This code allows a user to upload a photo and insert a moment on to their Google + profile that links to that photo.

To run this code, follow these steps:

1. Install, create, and activate a virtual environment in the directory:
	
	```
	$ pip install virtualenv
	$ virtualenv venv
	$ . venv/bin/activate
	```

	You can read more on virtual environments here: 
	http://docs.python-guide.org/en/latest/dev/virtualenvs/

2. Once the virtual environment is activated, install the requirements:
	
	```
	$ pip install -r requirements.txt
	```

3. Call the script
	
	```
	$ python signin.py
	```

4. Navigate to http://localhost:4567/

5. Sign in with a Google+ account

6. Navigate to http://localhost:4567/moment to insert a "moment" on to your profile

7. To view the moment:
	- Go to the "About" tab of your Google+ profile.
	- Scroll down to "Apps with Google+ Sign-in"
	- Click "Project Default Service Account"

Instructions

To run this website, it needs to run on a local server and it will be running the application from a virtual environment so that all packages will be already pre-installed within the whole folder itself.

To run the virtual environment do the following (instructions for windows OS only), start with going into command prompt:

1. Go into the 'flask_forum_env' folder
2. Enter 'venv\Scripts\activate' to activate the virtual environment
3. Go to the following path: flask_forum_env (folder) > Flask Forum (folder)
4. Enter 'python run.py' to run the local server
5. Go to the web browser's url and enter the following: 'http://localhost:8080/'

If you want to change the port number for the localhost, go to the following path: flask_forum_env (folder) > Flask Forum (folder) > run.py . Look for the code 'app.run(debug=True, port=8080)' on line 12 and change the 'port' parameter 
(localhost uses port number 8080 by default)

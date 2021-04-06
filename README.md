# Python Flask web-application for managing documents

# Exercise 
Please write a small web-application for managing documents with a python backend.

For the purposes of this exercise, please use SQLite as the database.

The application should have the following functionality:

* The user should be able to log-in (sign-up form is optional. It's also ok to pre-create user accounts).
* The following functionality should only be available to logged in users:
* The user should be able upload a PDF document.
* The uploaded documents entries should be shown in a table. Users should only be able to see their own documents.
* The user should be able to download the uploaded documents.
* The user should be able to add an arbitrary number of attributes (key-value pairs) to the document.
* The user should be able to edit and remove existing attributes.
* The user should be able to remove existing documents.
* The user should be able to trigger a (dummy) OCR analysis. The result of this analysis should be persisted in the database and shown in the UI.

Please use the following function to simulate the OCR analysis:
```
def run_ocr(document):
    time.sleep(120)
    return {
        "extracted_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    }
```

The styling of the UI is not important for this exercise, so feel free to use unstyled HTML or any UI library you are familiar with.

Feel free to layout the UI as you see fit.

Feel free to use utility libraries or frameworks, but please specify any dependencies in a requirements.txt or package.json.

Please write instructions on how to build and run this project.

Please don't spend more than ca. 4 hours on this project.

If you feel like you need to skip certain aspects of the implementation due to lack of time, please write some comments on how you would approach the problem. 

# Prequisites for running the web-application
1. Clone the git repository
1. Prepare conda or venv environment and install the required packages using conda or pip
   * [conda_requirements.txt](conda_requirements.txt)
   * [pip_requirements.txt](pip_requirements.txt)
1. Navigate to the project root directory
1. Run the flask application 
 Windows CMD
 ```
 set FLASK_APP=app.py
 flask run
 ```
 Linux
 ```
 export FLASK_APP=app.py
 python -m flask run
 ```
1. Manually add users to the database
 The application does not provide any sign-up form. That's why it is required to manually add users in the database by executing the following script:
 ```
 python create_db.py
 ```
1. Login
 Open the URL off your Flask server, e.g. http://127.0.0.1:5000/
 Enter the credentials of an user you previously created.

# Basic functionality implemented
* Login
* Upload of an document
* List uploaded documents 
* Run dummy OCR analysis
* Logout

# Additional notes
* Approx. 5 hours spent on coding and additionally some time for Git upload and documentation 
* No sign-up form exists
* Uploaded documents will be saved on disk of Flask server; The database just stores an id, file name and user_id (owner) for each uploaded document
* Possible database model prepared for adding arbitrary key-value pairs to a document 
* Not implemented: Delete document, donwload document, Add document attributes, Edit document attributes, Delete document attributes, List document attributes
* No caching is implemented

# Sources used for development:
* https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#simple-relationships
* https://docs.sqlalchemy.org/en/13/_modules/examples/vertical/dictlike.html
* https://docs.sqlalchemy.org/en/13/orm/collections.html#dictionary-collections
* https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html#proxying-to-dictionary-based-collections
* https://flask-login.readthedocs.io/en/latest/
* https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
* https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
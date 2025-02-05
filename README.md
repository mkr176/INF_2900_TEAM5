<p align="center">
  <img src="library_manager\frontend\public\images\library_seal.jpg" alt="docu_llama" width="300"/>
  <br>
</p>

# LibManager
Agile Software Engineers and Inventors: Alvaro, Carlos, Julius, Matt

## Documentation
[LateX Link](https://sharelatex.tum.de/1436619729gkstxqtxbvgv)

[Docs (Userstories, personas etc)](docs/README.md)

## Running the project

To run the project, you will need to run the following commands in your first terminal:

1. NOTE: Continue the rest in your second termnial:  
    To install all requierd npm packages, navigate to the `library_manager/frontend/` folder and run the following:
   ```bash
   npm install
   ```
2. To start the React server, in the same folder run the command:. Note: The listed server does not serve static files managed by Django. It's specifically for developing the React frontend.
   ```bash
   npm run dev
   ```
3. To start the Django server, navigate to the `backend` folder and run the following command:
   ```bash
   python manage.py runserver
   ```
4. Open your browser and navigate to `http://localhost:8000/` (where the Django server is being hosted) to view the project. Or The port that is displayed on your terminal

## Pre-requisites

To run this project, you will need to have the following installed:

- [Node.js](https://nodejs.org/en/)
- [npm](https://www.npmjs.com/)
- [Python](https://www.python.org/)

You will also need to install the following python packages:

- Django (v5.0.1)
- WhiteNoise (v6.6.0)

### Python Virtual Environment

To run the project and install these python packages, it is recommended to use a virtual environment. Follow the steps below to create and activate a virtual environment.

1. To create a virtual environment, run the following command in your terminal:
   ```bash
   python -m venv venv
   ```
2. Then activate the virtual environment(FOR LINUX):

   ```bash
   source venv/bin/activate
   ```

   FOR WINDOWS

   ```bash
   venv\Scripts\activate
   ```

   or

   ```
   .\env\Scripts\activate
   ```

3. To install the required python packages, run the following command:
   ```bash
   pip install -r requirements.txt
   ```


## Git Workflow

### Push to main from branch

To push changes from your branch to the main branch, you'll need to follow these steps using Git:

1. Ensure you are in your branch:

   ```bash
   git checkout <your-branch-name>
   ```

2. Commit your changes:

   ```bash
   git add <what-you-are-adding>
   git commit -m "Your commit message"
   ```

3. Push changes to your remote branch:

   ```bash
   git push origin <your-branch-name>
   ```

4. Switch to the "main" branch:

   ```bash
   git checkout main
   ```

5. Pull the latest changes from the remote "main" branch:

   ```bash
   git pull origin main
   ```

6. Merge your branch into "main":

   ```bash
   git merge <your-branch-name>
   ```

7. Push the changes to the remote 'main' branch:
   ```bash
   git push origin main
   ```

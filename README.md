<p align="center">
  <img src="library_manager\frontend\public\images\library_seal.jpg" alt="docu_llama" width="300"/>
  <br>
</p>

# LibManager

Agile Software Engineers and Inventors: Alvaro, Carlos, Julius, Matt

## Documentation

[LateX Link](https://sharelatex.tum.de/1436619729gkstxqtxbvgv)

[Docs (old, rather use the LaTeX Link above for user stories, features etc.)](docs/README.md)

## Pre-requisites

To run this project, you will need to have the following installed:

- [Node.js](https://nodejs.org/en/)
- [npm](https://www.npmjs.com/)
- [Python](https://www.python.org/)

You will also need to install the following python packages:

- Django (v5.0.1)
- WhiteNoise (v6.6.0)

### Python Virtual Environment

#### Automatic Routine
##### Windows

1.  **`Windows_start_backend.bat`**: Starts the Django backend server.
    *   Double-click `Windows_start_backend.bat` or run it from the command prompt in the project root by typing `Windows_start_backend.bat` and pressing Enter.

2.  **`Windows_start_frontend.bat`**: Starts the React frontend server in a **new terminal**.
    *   Open a **new Command Prompt or PowerShell window**, navigate to the project root, and run the script by typing `Windows_start_frontend.bat` and pressing Enter.

##### Linux/Mac

1.  **`Linux_start_backend.sh`**: Starts the Django backend server.
    *   Make the script executable: `chmod +x Linux_start_backend.sh`
    *   Run the script from the project root: `./Linux_start_backend.sh`

2.  **`Linux_start_frontend.sh`**: Starts the React frontend server in a **new terminal**.
    *   Make the script executable: `chmod +x Linux_start_frontend.sh`
    *   Open a **new terminal window**, navigate to the project root, and run the script: `./Linux_start_frontend.sh`


#### Manual Routine
To run the project and install these python packages, it is recommended to use a virtual environment. Follow the steps below to create and activate a virtual environment.

1. Create & Activate Virtual Environment:
   Navigate to INF_2900_TEAM5:
   For Linux/Mac:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
   ```

   For Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate

   ```

2. To install the required python packages, run the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. Change directory to `library_manager` and Run Database Migration

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. If Any error occurs, Check if MySQL Server is Running

Run the following command to check if MySQL is running inside WSL:

Linux:

```bash
sudo service mysql status
```

Windows:

```
Get-Service -Name MySQL*
```

5. If MySQL is Not Running, start it and run step 3 again.

Start it with:

```bash
sudo service mysql start
```

Windows:
If you don’t know the exact MySQL service name, you can list all services:

```bash
Get-Service | Select-String "MySQL"
```

```bash
Start-Service -Name MySQL80  # Change "MySQL80" if your service has a different name
```

6. To start the Django server. run the following command:
   ```bash
   python manage.py runserver
   ```

## Running the Frontend

To run the frontend , you will need to run the following commands in NEW terminal:

1. NOTE: Continue the rest in your second termnial:  
    To install all requierd npm packages, navigate to the `library_manager/frontend` folder and run the following:
   ```bash
   npm install
   ```
2. To start the React server, in the same folder run the command:. Note: The listed server does not serve static files managed by Django. It's specifically for developing the React frontend.
   ```bash
   npm run dev
   ```
3. Open your browser and navigate to [http://localhost:8000/](http://localhost:8000/)
4.

## DATABASE CONNECTIONS

First download the version OF (mysql-installer-community-8.0.41.0.msi) [352.2m](https://dev.mysql.com/downloads/installer/)

When you are installing it only install the MySQLServer version 8.0.41 and the MySQL Workbench 8.0.41
The password should be SoftwareUser
The only things that should be change is the port to 3305.

These are the only changes that you must do when you are installing MySQL

When you start MySQL you should run and create a database called:

- CREATE DATABASE library

Then connect to the database.

When it finish all the instalation and after you install the `requirements.txt` in the terminal you should enter while you are in `library_manager`:

- python manage.py makemigrations

And after that it will show that: No changes detected. Then you should run:

- python manage.py migrate

And then finally you can run the server:

- python manage.py runserver

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

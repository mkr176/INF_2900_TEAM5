# Solution for WSL: Install MySQL Devewlopment Libraries

Since you are using WSL (Linux), follow these steps:

### 1. Update Your Package List

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install MySQL Client and Development Headers

```
sudo apt install default-libmysqlclient-dev build-essential pkg-config -y
```

### 3. Try Installing mysqlclient Again

Now, activate your virtual environment and reinstall mysqlclient:

```bash
source venv/bin/activate  # Activate your virtual environment
pip install mysqlclient
```

OR reinstall all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

## Alternative: Use pymysql Instead of mysqlclient

### 1. Install pymysql

```bash
pip install pymysql
```

### 2. Modify settings.py to Use pymysql

At the top of settings.py, add:

```
import pymysql
pymysql.install_as_MySQLdb()
```

Then restart your Django server:

```bash
python manage.py runserver
```

## Check if MySQL Server is Running

Run the following command to check if MySQL is running inside WSL:

```bash
sudo systemctl status mysql
```

or

```bash
sudo service mysql status
```

## If MySQL is Not Running

Start it with:

```bash
sudo systemctl start mysql
```

or

```bash
sudo service mysql start
```

## Check if MySQL is Listening on the Right Port

Your settings.py has this configuration:

```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'library',
        'USER': 'root',
        'PASSWORD': 'SoftwareUser',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Check If MySQL is Running on Port 3305

Run:

```
sudo netstat -tulnp | grep mysql
```

or

```bash
sudo ss -tulnp | grep mysql
```

## Ensure MySQL User Has Access

Your USER: 'root' might not have permission to access MySQL from your WSL environment.

### GrantAccess to Root User.

1. Login to MySQL:

```bash
sudo mysql -u root -p
```

2. Run the following SQL commands:

```
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'SoftwareUser';
FLUSH PRIVILEGES;
```

3. Restart MYSQL:

```
sudo systemctl restart mysql
```

## Try Connecting Manually to MySQL

To check if the connection works, run:

```bash
mysql -u root -p -h 127.0.0.1 -P 3306
```

If this command fails, your MySQL server is not running on the right port. Change the port to 3306 in settings.py and try again.

## Final Step

Once MySQL is properly installed and mysqlclient or pymysql is set up, run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

| Issue                               | Solution                                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------------------------ |
| MySQL server is not running         | Start MySQL using sudo systemctl start mysql                                               |
| MySQL is running on a diffrent port | Change port to 3306 in settings.py                                                         |
| Root user has no access             | Run ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'SoftwareUser'; |
| localhost isn't working             | Change HOST to 127.0.0.1 in settings.py                                                    |

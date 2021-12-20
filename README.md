# Demo project for database course

## Setup Instructions:

1. download and unzip this repo

2. import into visual studio code

3. create python virual enviornment \
```python -m venv env```
   
4. activate the python virual enviornment \
   (for windows): ```.\env\Scripts\activate``` \
   (for mac): ```source env/bin/activate```
   
5. upgrade the pip \
```python -m pip install --upgrade pip```

6. install required libraries \
```pip install -r requirements.txt```

7. add/modify db.yaml file accordingly

8. create accounts table in aws mysql database \
```CREATE TABLE `feitian`.`accounts` ( `id` INT NOT NULL AUTO_INCREMENT, `fullname` VARCHAR(255) NULL, `username` VARCHAR(255) NULL, `password` VARCHAR(255) NULL, `email` VARCHAR(255) NULL, PRIMARY KEY (`id`));```

9. run the app \
```python app.py```
   
10. CTRL+C to quit and type ```deactivate```

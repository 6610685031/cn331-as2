# CN331-AS2 (Create Django Web App)
6610685031 Krittin Dansai\
6610545029 Thawalporn Jindavaranon


link video: <https://youtu.be/g87WBwF8XG0>
## Cloning this repository
```
git clone https://github.com/6610685031/cn331-as2
cd cn331-as2
```

## Setting up Virtual Environment
```
python -m venv .venv
```
Activate virtual enviroment (for bash, unix-system alike)
```
source .vnev/bin/activate
```
and for Windows
```
.venv\Scripts\activate.bat
```
## Installing from requirements.txt
```
pip install -r requirements.txt
```
If you don't have pip installed, please refer to the Python official website: https://packaging.python.org/en/latest/tutorials/installing-packages/

## Create new database migrations (this is required for first time usage)
```
cd classbooking
python manage.py makemigrations
python manage.py migrate
```

## Running the web server
```
python manage.py runserver
```

## Creating Superuser (this is required for accessing admin pages)
```python manage.py createsuperuser```

## Flush Database (for safety reasons)
```python manage.py flush```
for deployment purposes


# CN331-AS2 (Create Django Web App)
THIS README.md IS INCOMPLETE AND NEED INCREMENTAL UPDATES
FOR NOW HERE'S HOW TO DEPLOY BASIC DJANGO APP

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

## Running the web server
```
cd classbooking
python manage.py runserver
```

## Flush Database (for safety reasons)
```python manage.py flush```
for deployment purposes

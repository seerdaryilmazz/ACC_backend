## AccompanyBackend

### Setup (MacOS)
- Clone this repository

- Create a virtualenv on the same path with run.py:
```
python3 -m venv venv
```
- Activate venv
```
source venv/bin/activate
```
- Install packages
```
pip install -r requirements.txt
```

- Run:
```
python run.py
```

- Each namespace under apis package has following structure and it helps us to manage project easier:
```
-- package_name
----- __init__.py
----- api.py
```

### Current Pages

- Swagger: http://0.0.0.0:5000/api/v1/docs
- Base route: http://0.0.0.0:5000/api/v1/
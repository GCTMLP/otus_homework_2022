# Hasker
poor man`s stackoverflow

# Online version
https://gctmlp.ru/

# About

This is educational project, which functional is similar to stackoverflow.com

Technology stack is:
  - Nginx
  - uWSGI
  - Django
  - Vue.js
  - MySQL
  - Smarty templates

# How to deploy

1. Clone the repository
```
git clone https://github.com/GCTMLP/otus_hasker.git
```
```
cd otus-hasker
```

2. Install requirements
```
pip3 install -r requirements.txt
```

3. Create database named "hasker"
```
mysql -u "username" -p
create database hasker;
```

4. Write your mysql configuration at "config/settings.py"
examlpe:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hasker',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': 'yourhost' (ex: localhost),
        'PORT': 'yourport',
    }
}
```

5. Apply migrations
```
python3 manage.py makemigration
python3 manage.py migrate
```

6. Add your server name at "config/settings.py"
example
```
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'gctmlp.ru']
```
7. Set up email delivery 
```
EMAIL_HOST = 'your_email_host'  ex: 'smtp.gmail.com'
EMAIL_HOST_USER = 'your_user_email'
EMAIL_HOST_PASSWORD = 'your_password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

8. Set up nginx
example configuration at "/etc/nginx/sites-enabled/hasker"
```
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/yourcrt.crt;
    ssl_certificate_key /etc/ssl/yourkey.key;
    server_name yourservername;

    location / {
       uwsgi_pass unix:///run/uwsgi/app/hasker/socket;
       include uwsgi_params;
       uwsgi_read_timeout 300s;
       client_max_body_size 32m;
    }

    location  /static/ {
         alias /hasker_project/hasker/static/;
    }

    location /media/ {
        alias /hasker_project/hasker/media/;
    }
}
```

9. Import styles from ```https://github.com/GCTMLP/html_styles``` and add them to hasker/static/assets

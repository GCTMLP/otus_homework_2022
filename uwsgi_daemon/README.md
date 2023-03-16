# uwsgi_deamon
Weather uWSGI daemon. Determines the city by IP and get information about the weather in given cit

# Requirements
  - CentOS 7
  - python3
  - python-requests
  - nginx
  - git

# How to deploy

1. On CentOS Virtual Machine install and setting up git
```
sudo yum install git
```
```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

2. Clone project
```
git clone https://github.com/GCTMLP/uwsgi_deamon.git
```

3. Go to project folder
```
cd uwsgi_deamon
```

4. Compile package
```
./buildrpm.sh ip2w.spec
```
You can find your rpm file in RPMS folder

Also you can clone rpm file from my repository ```https://github.com/GCTMLP/uwsgi_deamon.git```

# run deamon 
```sudo yum install /path_to_rmp_file/your_file.rpm```

```systemctl start ip2w```

# example 
query:
```curl http://localhost/ip2w/176.14.221.123```

answer:
```{"city": "Moscow", "temp": "+20", "conditions": "небольшой дождь"}```

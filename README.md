# fast_api_no_linkedin

<div align="center">
  <img src="https://github.com/netox64/fast_api_web/blob/main/docs/ft01.png" width="250" height="250" />
  <img src="https://github.com/netox64/fast_api_web/blob/main/docs/ft02.png" width="250" height="250" />
</div>

<h4 align="center">This project is the beginning of a backend, it only serves as a demonstration of things we can do with Python, and to train the language that now works in Excel Etals...</h4>

<p align="center">
<img src="https://sonarcloud.io/api/project_badges/measure?project=netox64_fast_api_web&metric=alert_status">
<img src="https://sonarcloud.io/api/project_badges/measure?project=netox64_fast_api_web&metric=coverage">
<img src="https://sonarcloud.io/api/project_badges/measure?project=netox64_fast_api_web&metric=duplicated_lines_density">
<img src="https://sonarcloud.io/api/project_badges/measure?project=netox64_fast_api_web&metric=security_rating">
<img src="https://sonarcloud.io/api/project_badges/measure?project=netox64_fast_api_web&metric=sqale_index">
</p>

<p align="center">
    <a href="#Technologies_Used">Technologies Used</a> •
    <a href="#Api_resources">Api resources</a> •
    <a href="#Folder_Architecture">Folder Architecture FrontEnd</a> •
    <a href="#Folder_Architecture">Folder Architecture BackEnd</a> •
    <a href="#Running_Application">Running application</a> •
    <a href="#About_the_Author">About the Author</a> •
    <a href="https://github.com/netox64/fast_api_web/blob/main/LICENSE">Licensing</a>
</p>

## Technologies_Used

- Python.
- Fast API, webdrive, selenium, bs4...

## Prerequisites

- have python installed on the machine, the virtualenv creation module
- docker and docker compose installed
- create database fast_api


## Running_Application

- create virtual env
```
   sudo apt install python3.12-venv &&
   python3 -m venv venv
```

- activate venv
```
   source venv/bin/activate

```

- create database in dbeaver with postgres of name fast_api

- install dependencies e create and create tables
```
   docker-compose up -d && python create_main.py &&
   pip install -r requirements.txt
```

- run docs
```
   uvicorn main:app --reload
```

- go

http://localhost:8000/docs


## About_the_Author
- Clodoaldo Neto :call_me_hand:
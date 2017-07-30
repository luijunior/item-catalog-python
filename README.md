# Item Catalog APP #

### Project from udacity Full stack web developer ###

### How do I get set up? ###

* Clone the repository OR Unzip the file
* Have Docker installed
* Run the sequence bellow
```python
cd projectitemcatalog
docker build -t item-catalog-python:1.0.0-RELEASE .
docker-compose up
```

Open in browser -> http://localhost:5000

### Adding Categories and Items ###

In the setup_db.json you can add new items and categories that will be included in the image os the app
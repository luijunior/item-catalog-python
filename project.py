#!/usr/bin/env python3
import models
import database_setup

if __name__ == '__main__':
    models.create_tables()
    database_setup.insert_some_items()

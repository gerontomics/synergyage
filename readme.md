What is SynergyAge?
===============

SynergyAge database hosts high-quality, manually curated information about the synergistic and antagonistic lifespan effects of genetic interventions in model organisms, also allowing users to explore the longevity relationships between genes in a visual way.

Preview
---------------------
[SynergyAge.info](http://synergyage.info)

Python dependencies
---------------------
The dependencies required for the website are included in the repository's `requirements.txt` file.

Environment Variables
---------------------

The following environment variables are required:

`DATABASE_URL`
    - database connection URI string.

`RECAPTCHA_SECRET_KEY`
    - Google reCAPTCHA secret key.

Database
---------------------

The `.pgsql` database file generated by `pg_dump` is stored in root directory and it's named `database.pgsql`.

Database contains one superuser account, with the following credentials:

    Username: test
    Password: synergyage123.

Contributing
---------------------

Contributions, issues and feature requests are welcome.

Author
---------------------
**Systems Biology of Aging Group**

- Website: [Aging-Research.Group](http://www.aging-research.group/)


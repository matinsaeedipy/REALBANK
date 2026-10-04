#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simbank.settings")
    # Local development convenience: `runserver` runs in DEBUG mode over plain HTTP.
    # Production servers use gunicorn (see Dockerfile / Procfile) and stay in safe mode.
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        os.environ.setdefault("DJANGO_DEBUG", "1")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

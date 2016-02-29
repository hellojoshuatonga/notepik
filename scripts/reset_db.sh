#!/bin/bash

# Script to use a new database
# Run this command in root project directory

echo "[!] Deleting migrations from main app..."
rm main/migrations/* &> /dev/null

#echo "[!] Deleting database..."
#rm db.sqlite3


echo "[!] Deleting all tables from database...";
echo "yes" | ./manage.py reset_db


echo "[+] Making migrations for main app..."
./manage.py makemigrations main

echo "[+] Migrating..."
./manage.py migrate



#echo "[+] Copying custom migrations to default migrations folder..."
#cp main/custom_migrations/* main/migrations/

#echo "[+] Updating migrations for main app..."
#./manage.py makemigrations main

#echo "[+] Migrating..."
#./manage.py migrate


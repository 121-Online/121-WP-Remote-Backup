"""
WP Remote FTP Backup

@category    Backup Solutions
@package     WP Remote FTP Backup
@subpackage  WordPress Backup Manager
@license     GPLv2 <https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html>
@author      James Gibbons <jgibbons@121digital.co.uk>
@link        https://www.121digital.co.uk

121Domains is a trading name of 121 Digital Services Limited.

Disclaimer: This source code and its comments are the intellectual property of 121Domains, 
a trading name of 121 Digital Services Limited. It is free to use, modify, and distribute under the terms 
of the GNU General Public License version 2 (GPLv2).

Description:
WP Remote FTP Backup is an open-source project created by 121 Digital Services Limited. 
This Python script automates the backup process for WordPress websites. It performs the following tasks:

1. Backs up the WordPress site files and MySQL database.
2. Compresses the backup into a zip file.
3. Stores the backup locally, with an option to delete the previous day's backup.
4. Uploads the backup to a remote FTP server.
5. Manages old backups on the FTP server, retaining only the most recent backups based on the configurable retention policy.
6. Logs all actions to a log file for auditing and troubleshooting purposes.

This script is intended for use by WordPress site administrators who need an automated, reliable backup solution with remote storage capabilities.
"""

import os
import zipfile
import shutil
import subprocess
from ftplib import FTP
from datetime import datetime, timedelta

# Configuration variables
wp_directory = '/path/to/wordpress'
backup_directory = '/path/to/backup'
log_file = os.path.join(backup_directory, 'backup_log.txt')
database_config = {
    'host': 'localhost',
    'user': 'your_db_user',
    'password': 'your_db_password',
    'database': 'your_db_name'
}
ftp_config = {
    'host': 'ftp.example.com',
    'user': 'ftp_user',
    'password': 'ftp_password',
    'remote_dir': '/remote/backup/directory',
    'keep_days': 3  # Number of days to keep backups on FTP, set to 0 to disable deletion
}

def log_message(message):
    """
    Logs a message with a timestamp to the log file.
    
    :param message: Message to be logged.
    """
    with open(log_file, 'a') as log:
        log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def delete_yesterdays_backup():
    """
    Deletes the backup file from yesterday based on the file name.
    
    - The backup file name includes the date in the format 'YYYYMMDD'.
    - Only yesterday's backup will be deleted, ensuring that only the current backup is stored.
    """
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    backup_to_delete = f'wordpress_backup_{yesterday_str}.zip'
    
    backup_file_path = os.path.join(backup_directory, backup_to_delete)
    
    if os.path.exists(backup_file_path):
        os.remove(backup_file_path)
        log_message(f"Deleted yesterday's backup file: {backup_to_delete}")
    else:
        log_message("No backup found to delete for yesterday.")

def backup_site():
    """
    Backup the WordPress site files and MySQL database.
    
    - Copies the WordPress directory to a specified backup directory.
    - Creates a SQL dump of the MySQL database using `mysqldump`.
    - Creates separate directories for site data and database within the backup directory.
    """
    log_message("Starting backup process.")
    
    site_backup_dir = os.path.join(backup_directory, 'site_data')
    db_backup_dir = os.path.join(backup_directory, 'database')
    os.makedirs(site_backup_dir, exist_ok=True)
    os.makedirs(db_backup_dir, exist_ok=True)

    # Copy WordPress files to the site_data backup directory.
    shutil.copytree(wp_directory, site_backup_dir, dirs_exist_ok=True)
    log_message("WordPress files copied successfully.")
    
    # Create a SQL dump of the MySQL database.
    backup_file = os.path.join(db_backup_dir, 'database_backup.sql')
    dump_command = [
        'mysqldump',
        '-h', database_config['host'],
        '-u', database_config['user'],
        f"--password={database_config['password']}",
        database_config['database'],
        '--result-file', backup_file
    ]
    
    try:
        subprocess.run(dump_command, check=True)
        log_message("Database SQL dump completed successfully.")
    except subprocess.CalledProcessError as e:
        log_message(f"Error during database dump: {e}")

def zip_backup():
    """
    Zip the backup directories into a single file.
    
    - Compresses the site_data and database directories into a single zip file.
    - The zip file is created in the specified backup directory with a timestamped filename.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    zip_file = os.path.join(backup_directory, f'wordpress_backup_{date_str}.zip')

    with zipfile.ZipFile(zip_file, 'w') as backup_zip:
        for root, dirs, files in os.walk(os.path.join(backup_directory, 'site_data')):
            for file in files:
                backup_zip.write(os.path.join(root, file),
                                 os.path.relpath(os.path.join(root, file),
                                                 os.path.join(backup_directory, 'site_data')))
        for root, dirs, files in os.walk(os.path.join(backup_directory, 'database')):
            for file in files:
                backup_zip.write(os.path.join(root, file),
                                 os.path.relpath(os.path.join(root, file),
                                                 os.path.join(backup_directory, 'database')))
    log_message(f"Backup zipped successfully: {zip_file}")

def upload_backup():
    """
    Upload the backup zip file to a remote FTP server and manage old backups.
    
    - Connects to the FTP server using the provided credentials.
    - Uploads the generated zip file to the specified remote directory.
    - Deletes old backups from the FTP server based on the `keep_days` setting.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    zip_file = os.path.join(backup_directory, f'wordpress_backup_{date_str}.zip')

    ftp = FTP(ftp_config['host'])
    ftp.login(ftp_config['user'], ftp_config['password'])
    ftp.cwd(ftp_config['remote_dir'])
    
    # Upload the current backup
    with open(zip_file, 'rb') as f:
        ftp.storbinary(f"STOR {os.path.basename(zip_file)}", f)
    log_message(f"Backup uploaded to FTP server: {os.path.basename(zip_file)}")
    
    # Delete old backups from FTP if configured
    if ftp_config['keep_days'] > 0:
        cutoff_date = datetime.now() - timedelta(days=ftp_config['keep_days'])
        for filename in ftp.nlst():
            if filename.startswith('wordpress_backup_') and filename.endswith('.zip'):
                file_date_str = filename.split('_')[2].split('.')[0]
                try:
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                    if file_date < cutoff_date:
                        ftp.delete(filename)
                        log_message(f"Deleted old backup from FTP: {filename}")
                except ValueError:
                    log_message(f"Skipped FTP file with invalid date format: {filename}")

    ftp.quit()

def main():
    """
    Main function to execute the backup process.
    
    - Logs the start of the backup process.
    - Deletes yesterday's local backup.
    - Backs up the WordPress site files and database.
    - Compresses the backup into a zip file.
    - Uploads the zip file to a remote FTP server.
    - Manages old backups on the FTP server.
    """
    log_message("Backup script initiated.")
    delete_yesterdays_backup()
    backup_site()
    zip_backup()
    upload_backup()
    log_message("Backup process completed.")

if __name__ == "__main__":
    # Log the start of the script.
    log_message("\n--- Backup Script Run: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " ---\n")
    main()


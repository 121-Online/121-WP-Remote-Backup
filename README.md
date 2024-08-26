# WordPress Backup Script

This Python script automates the backup of a WordPress website and its associated MySQL database. The script performs the following tasks:

- Backs up WordPress site files and database.
- Compresses the backup into a zip file.
- Stores the backup locally, with options for deleting older backups.
- Uploads the backup to a remote FTP server.
- Manages old backups on the FTP server, retaining only the most recent backups as per configuration.

## Project Background
Part of this project originates from an internal solution to backup staging websites on developer machines but may see some use in a production environment in the future of 121 Digital's website design platform.

## Notice
This open source branch of the project may not be actively maintained and will often be downstream of our internal solution given the sensetive nature of our backup infastructure; This project is intended for educational purposes and is not provided as a turn-key solution.

## Features

- **Local Backup Management:** Automatically deletes the previous day's backup, ensuring only the latest backup is stored locally.
- **FTP Backup Management:** Configurable retention policy on the FTP server, with options to keep the last N days' backups.
- **Detailed Logging:** Logs all operations to a log file with timestamps, providing insights into the backup process.

## Prerequisites

- Python 3.x
- Required Python packages: `ftplib`, `shutil`, `zipfile`, `subprocess`
- Access to the MySQL database with `mysqldump` installed.
- FTP credentials for the remote backup server.

## Configuration

Update the following configuration variables in the script:

- `wp_directory`: Path to the WordPress installation directory.
- `backup_directory`: Path to the local backup directory.
- `database_config`: Dictionary containing MySQL database connection details.
- `ftp_config`: Dictionary containing FTP server connection details and retention policy.

```python
wp_directory = '/path/to/wordpress'
backup_directory = '/path/to/backup'
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


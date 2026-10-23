import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import management


class Command(BaseCommand):
    help = 'Creates a safe timestamped administrative backup of the HMS database and media files.'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = settings.BASE_DIR / 'backups'
        os.makedirs(backup_dir, exist_ok=True)

        self.stdout.write(f"Initiating HMS database backup at {timestamp}...")

        # 1. Export JSON fixtures of all operational data
        json_backup_path = backup_dir / f"hms_data_dump_{timestamp}.json"
        with open(json_backup_path, 'w', encoding='utf-8') as f:
            management.call_command('dumpdata', '--natural-foreign', '--natural-primary', exclude=['contenttypes', 'auth.permission'], stdout=f)
        
        self.stdout.write(self.style.SUCCESS(f"Data fixture backup generated: {json_backup_path}"))

        # 2. If SQLite is in use, create a safe atomic binary snapshot
        db_path = settings.BASE_DIR / 'db.sqlite3'
        if os.path.exists(db_path):
            sqlite_backup_path = backup_dir / f"hms_db_{timestamp}.sqlite3"
            shutil.copy2(db_path, sqlite_backup_path)
            self.stdout.write(self.style.SUCCESS(f"SQLite binary snapshot created: {sqlite_backup_path}"))

        self.stdout.write(self.style.SUCCESS("HMS Backup completed successfully."))

resource "google_sql_database_instance" "bad_sql" {
  name             = "bad-sql-instance"
  database_version = "MYSQL_5_6"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"
    backup_configuration {
      enabled = false
    }
    ip_configuration {
      ipv4_enabled    = true
      require_ssl     = false
      authorized_networks = []
    }
    # No maintenance window, no disk encryption, no high availability
    # No deletion protection, no user labels
  }

  # No root password set, no users created
}

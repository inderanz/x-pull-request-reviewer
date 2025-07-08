provider "google" {
  project = "test-gcp-project"
  region  = "us-central1"
}

resource "google_container_cluster" "primary" {
  name     = "primary-gke"
  location = "us-central1-a"

  # SECURITY ISSUE: No network policy enabled
  remove_default_node_pool = false

  node_config {
    # SECURITY ISSUE: Hardcoded service account
    service_account = "default-sa@test-gcp-project.iam.gserviceaccount.com"
    # COMPLIANCE ISSUE: No shielded nodes
    preemptible  = true
    # BEST PRACTICE: No labels
  }

  # SECURITY ISSUE: No master authorized networks
  # COMPLIANCE ISSUE: No private cluster
}

resource "google_sql_database_instance" "default" {
  name             = "mysql-instance"
  database_version = "MYSQL_5_7"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"
    # SECURITY ISSUE: Public IP enabled
    ip_configuration {
      ipv4_enabled    = true
      # SECURITY ISSUE: No authorized networks
    }
    # COMPLIANCE ISSUE: No backup configuration
  }
}

resource "google_storage_bucket" "open_bucket" {
  name     = "open-bucket-test"
  location = "US"
  force_destroy = true

  # SECURITY ISSUE: Public access
  uniform_bucket_level_access = false
}

resource "google_project_iam_member" "bad_admin" {
  project = "test-gcp-project"
  role    = "roles/owner"
  member  = "user:admin@example.com" # SECURITY ISSUE: Overly permissive
}

# BEST PRACTICE: No outputs, no variable validation, no documentation 
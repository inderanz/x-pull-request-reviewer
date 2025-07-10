resource "google_container_cluster" "bad_gke" {
  name     = "bad-gke-cluster"
  location = "us-central1"
  initial_node_count = 1

  node_config {
    machine_type = "e2-micro"
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    metadata = {
      disable-legacy-endpoints = "false"
    }
    preemptible = true
  }

  # Missing network config, no private nodes, no shielded nodes
  # No resource labels, no logging, no monitoring
  # No binary authorization, no master authorized networks
  # No release channel, no IP aliasing
}

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1
}

# Enable the web UI
ui = true

# prevent memory from being swapped to disk (security best practice)
disable_mlock = true

default_lease_ttl = "168h"
max_lease_ttl = "720h"
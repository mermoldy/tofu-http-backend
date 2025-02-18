terraform {
  backend "http" {
    address = "http://localhost:8000/state/project/1"
    # Optional: (Authentication token if implemented or any other required headers)
  }
}

resource "null_resource" "example" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "echo Hello from the custom HTTP backend for OpenTofu!"
  }
}

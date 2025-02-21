
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/project/1"
    lock_address   = "http://localhost:8000/state/lock/project/1"
    unlock_address = "http://localhost:8000/state/unlock/project/1"
    lock_method    = "POST"
    unlock_method  = "POST"
    username       = "scalr"
    password       = "scalr"
  }
}

resource "null_resource" "example" {
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    command = "sleep 10"
  }
}

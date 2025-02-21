
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/example/basic/1"
    lock_address   = "http://localhost:8000/state/lock/example/basic/1"
    unlock_address = "http://localhost:8000/state/unlock/example/basic/1"
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

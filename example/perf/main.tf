
terraform {
  backend "http" {
    address        = "http://localhost:8000/state/example/perf/1"
    lock_address   = "http://localhost:8000/state/lock/example/perf/1"
    unlock_address = "http://localhost:8000/state/unlock/example/perf/1"
    lock_method    = "POST"
    unlock_method  = "POST"
    username       = "scalr"
    password       = "scalr"
  }
}

resource "null_resource" "dummy" {
  count = 10000

  triggers = {
    id          = count.index
    always_run  = timestamp()
    long_string = <<EOT
      This is a very long string to increase state size. It contains multiple lines
      of text and repeated patterns to make the state file significantly larger.
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio.
      Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at
      nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec
      tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget
      nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra,
      per inceptos himenaeos. Curabitur sodales ligula in libero. Sed dignissim
      lacinia nunc. Curabitur tortor. Pellentesque nibh. Aenean quam. In scelerisque
      sem at dolor. Maecenas mattis. Sed convallis tristique sem.
    EOT

    big_map = jsonencode({
      key1 = "value1"
      key2 = "value2"
      key3 = "value3"
      key4 = "value4"
      key5 = "value5"
      nested = {
        nested_key1 = "nested_value1"
        nested_key2 = "nested_value2"
        long_list = [
          "item1", "item2", "item3", "item4", "item5",
          "item6", "item7", "item8", "item9", "item10"
        ]
      }
    })
  }
}

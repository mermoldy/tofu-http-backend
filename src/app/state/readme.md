# HTTP State

The application implements an HTTP state resource following [the HashiCorp specification](https://developer.hashicorp.com/terraform/language/backend/http).

> State will be fetched via GET, updated via POST, and purged with DELETE. The method used for updating is configurable.
> This backend optionally supports state locking. When locking support is enabled it will use LOCK and UNLOCK requests providing the lock info in the body. The endpoint should return a 423: Locked or 409: Conflict with the holding lock info when it's already taken, 200: OK for success. Any other status will be considered an error.
> The ID of the holding lock info will be added as a query parameter to state updates requests.

The remote storage is online minio service.

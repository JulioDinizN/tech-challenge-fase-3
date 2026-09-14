# Protected remote state bucket

Bootstrap used for this environment: create the private/versioned bucket with OCI CLI, initialize this root with its ignored backend.hcl, and import the bucket with `terraform import oci_objectstorage_bucket.state 'n/<namespace>/b/<bucket>'`. Verify a no-change plan. This keeps authoritative state remote from the first Terraform operation and avoids generating local bootstrap state. The bucket is subsequently managed by this root.

Core and platform initialize directly against this bucket with their own Object Storage keys. Never commit backend.hcl, real tfvars, kubeconfigs, state or saved plans. The bucket has prevent_destroy and is retained during application teardown; confirm residual objects/costs afterward.

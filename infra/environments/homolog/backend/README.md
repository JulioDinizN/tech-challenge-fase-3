# Protected remote state bucket

No command here has been executed against OCI. For a new bucket, in the future authorized window: initialize with `-backend=false`, apply only this root using an encrypted local working directory, then `terraform init -migrate-state -backend-config=backend.hcl` to move this bootstrap state into the bucket. Inspect the migration and protect/remove the local backup after verification. Core and platform always initialize directly with remote backends. If a suitable private/versioned bucket already exists, import it into this root instead of creating a duplicate, then migrate this root's state. Never leave final authoritative state local.

The bucket has `prevent_destroy`; keep it during application teardown. State and saved plans are private even when outputs omit passwords. Backend keys are separate for backend/core/platform.

from middlewared.rclone.base import BaseRcloneRemote
from middlewared.schema import Bool, Str


class SwiftRcloneRemote(BaseRcloneRemote):
    name = "SWIFT"
    title = "Swift"

    buckets = True

    rclone_type = "swift"

    credentials_schema = [
	Bool("env_auth", verbose="Get swift credentials from environment vars", default=False),
	Str("auth_version", verbose="Auth Version", enum=["1", "2", "3", ""], default=""),
	Str("auth", verbose="Auth URL", required=True),
	Str("endpoint_type", verbose="Endpoint type", enum=["public", "internal", ""], default="public"),
	Str("tenant_domain", verbose="Tenant Domain"),
	Str("tenant", verbose="Tenant Name"),
	Str("domain", verbose="User Domain"),
	Str("user", verbose="User Name", required=True),
	Str("key", verbose="API Key", required=True),
	Str("region", verbose="Region Name"),
    ]

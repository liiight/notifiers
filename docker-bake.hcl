# Local image builds: `docker buildx bake` builds ghcr.io/liiight/notifiers:dev for this machine.
# Published images are built by .github/workflows/docker.yml.

variable "VERSION" {
  default = "dev"
}

target "default" {
  dockerfile = "Dockerfile"
  tags       = ["ghcr.io/liiight/notifiers:${VERSION}"]
  args = {
    VERSION = VERSION
  }
}

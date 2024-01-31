
variable "GIT_COMMIT" {
  default = "latest"
}
variable "GIT_SOURCE" {
  default = ""
}
group "default" {
  targets = [
    "ml_api_base_amd64",
    "ml_api_base_arm64",
    "ml_api_amd64",
    "ml_api_arm64",
    ]
}


target "ml_api_base_amd64" {
  dockerfile = "Dockerfile.base_amd64"
  tags = ["ml_api_base:${GIT_COMMIT}-amd64"]
  platforms = ["linux/amd64"]
}

target "ml_api_base_arm64" {
  dockerfile = "Dockerfile.base_arm64"
  tags = ["ml_api_base:${GIT_COMMIT}-arm64"]
  platforms = ["linux/arm64"]
}

target "ml_api_amd64" {
  args = {
    GIT_COMMIT = "${GIT_COMMIT}"
    GIT_SOURCE = "${GIT_SOURCE}"
    ARCH = "amd64"
  }

  contexts = {
      "thespaghettidetective/ml_api_base:${GIT_COMMIT}-amd64" = "target:ml_api_base_amd64"
  }

  dockerfile = "Dockerfile"
  tags = ["ml_api:${GIT_COMMIT}-amd64"]
  platforms = ["linux/amd64"]
}

target "ml_api_arm64" {
  args = {
    GIT_COMMIT = "${GIT_COMMIT}"
    GIT_SOURCE = "${GIT_SOURCE}"
    ARCH = "arm64"
  }

  contexts = {
      "thespaghettidetective/ml_api_base:${GIT_COMMIT}-arm64" = "target:ml_api_base_arm64"
  }

  dockerfile = "Dockerfile"
  tags = ["ml_api:${GIT_COMMIT}-arm64"]
  platforms = ["linux/arm64"]
}

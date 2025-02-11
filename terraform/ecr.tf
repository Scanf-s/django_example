resource "aws_ecr_repository" "ecr_library" {
  name                 = "library"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
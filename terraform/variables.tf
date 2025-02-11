variable "aws_region" {
  type = string
  default = "ap-northeast-2"
}

# 반드시 terraform 사용 이전, prod.tfvars를 생성하여 본인 컴퓨터에 할당된 IPv4 주소를 넣어주어야 합니다. subnet은 반드시 32로 고정
variable "your_computer_ipv4_address" {
  type = string
}

variable "default_aws_region_az" {
  type = string
  default = "ap-northeast-2a"
}

variable "ec2-ami" {
  type = string
  default = "ami-037f2fa59e7cfbbbb"
}

variable "ec2-key-pair" {
  type = string
  default = "library"  # 반드시 terraform 사용 이전, AWS에 library 이름의 키페어를 생성해놓아야 합니다
}
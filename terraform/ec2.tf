resource "aws_instance" "library_backend" {
  ami = var.ec2-ami
  instance_type = "t2.micro"
  key_name = var.ec2-key-pair

  subnet_id = aws_subnet.library_public_subnet.id
  vpc_security_group_ids = [aws_security_group.library_sg.id]
  tags = {
    Name = "library_backend"
  }
}

resource "aws_eip" "library_backend_fixed_ipv4" {
  instance = aws_instance.library_backend.id
  domain = "vpc"

  tags = {
    Name = "library_eip"
  }
}

output "ec2_public_ipv4" {
  value = aws_eip.library_backend_fixed_ipv4.public_ip
}

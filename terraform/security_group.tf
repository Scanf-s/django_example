resource "aws_security_group" "library_sg" {
  name        = "library_sg"
  description = "Allow Djnago and SSH inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.library_vpc.id

  tags = {
    Name = "library_sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "allow_django_port" {
  security_group_id = aws_security_group.library_sg.id
  cidr_ipv4         = var.your_computer_ipv4_address
  from_port         = 8000
  ip_protocol       = "tcp"
  to_port           = 8000
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh_port" {
  security_group_id = aws_security_group.library_sg.id
  cidr_ipv4         = "0.0.0.0/0" # Github actions에서 접근이 가능해야 함
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_ingress_rule" "allow_grafana_port" {
  security_group_id = aws_security_group.library_sg.id
  cidr_ipv4         = "0.0.0.0/0" # 외부에서 접근이 가능해야함 (본인만 접근하는거면 django처럼 지정해도 됨)
  from_port         = 3000
  ip_protocol       = "tcp"
  to_port           = 3000
}

resource "aws_vpc_security_group_ingress_rule" "allow_cadvisor_port" { # 필요는 없는데, 브라우저로 접근해서 동작하는지 확인하려고 넣었음
  security_group_id = aws_security_group.library_sg.id
  cidr_ipv4         = "0.0.0.0/0" # 외부에서 접근이 가능해야함 (본인만 접근하는거면 django처럼 지정해도 됨)
  from_port         = 3000
  ip_protocol       = "tcp"
  to_port           = 3000
}

resource "aws_vpc_security_group_egress_rule" "default_egress" {
  security_group_id = aws_security_group.library_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}

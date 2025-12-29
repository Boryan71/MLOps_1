# Прописываем информацию о сети и подсети для ВМ
resource "yandex_vpc_network" "network-main" {
  name = var.network_name
}

resource "yandex_vpc_subnet" "subnet-a" {
  name           = "subnet-a"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network-main.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

#resource "yandex_vpc_subnet" "subnet-b" {
#  name           = "subnet-b"
#  zone           = "ru-central1-b"
#  network_id     = yandex_vpc_network.network-main.id
#  v4_cidr_blocks = ["192.168.10.13/24"]
#}

#resource "yandex_vpc_subnet" "subnet-c" {
#  name           = "subnet-c"
#  zone           = "ru-central1-c"
#  network_id     = yandex_vpc_network.network-main.id
#  v4_cidr_blocks = ["192.168.10.0/24"]
#}
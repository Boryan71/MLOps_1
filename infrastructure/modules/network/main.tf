terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

# Вписываем информацию об облачном провайдере
# Добавляем ID облака, каталога и зону достпуности ВМ
# Также вписываем файл ключа сервисного пользователя
provider "yandex" {
  cloud_id  = "b1gjkmtbqtvi36bqg5lt"
  folder_id = "b1ghtkl7gem9bo4hcudb"
  zone      = "ru-central1-b"
  service_account_key_file = "key.json"
#  token = ""
}

# Вписываем информацию о диске для ВМ
resource "yandex_compute_disk" "boot-disk-1" {
  name     = "boot-disk-1"
  type     = "network-ssd"
  zone     = "ru-central1-b"
  size     = "20"
  image_id = "epdldvlla2fgcbkc11e5"
}

# Прописываем информацию о сети и подсети для ВМ
resource "yandex_vpc_network" "network-1" {
  name = "network1"
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = "subnet1"
  zone           = "ru-central1-b"
  network_id     = yandex_vpc_network.network-1.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

# Вписываем информацию о виртуальной машине
resource "yandex_compute_instance" "vm-1" {
  name = "terraform1"
  resources {
    cores  = 2
    memory = 2
  }
  boot_disk {
    disk_id = yandex_compute_disk.boot-disk-1.id
  }
  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat       = true
  }
  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/ssh-key-1766963389342.pub")}"
  }
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}
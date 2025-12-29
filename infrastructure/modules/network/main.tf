terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  
  backend "s3" {
    endpoints = {
      s3 = "https://storage.yandexcloud.net"
    }
    bucket = "my-bucket-for-state"
    region = "ru-central1"
    key    = "terraform.tfstate"

    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true # Необходимая опция Terraform для версии 1.6.1 и старше.
    skip_s3_checksum            = true # Необходимая опция при описании бэкенда для Terraform версии 1.6.3 и старше.

  }
  
  required_version = ">= 0.13"
}

# Вписываем информацию об облачном провайдере
# Добавляем ID облака, каталога и зону достпуности ВМ
# Также вписываем файл ключа сервисного пользователя
provider "yandex" {
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.default_zone
  service_account_key_file = "key.json"
#  token = ""
}

# Вписываем информацию о диске для ВМ
resource "yandex_compute_disk" "boot-disk-1" {
  name     = "boot-disk-1"
  type     = "network-ssd"
  zone     = var.default_zone
  size     = "20"
  image_id = "fd85reopjehngttvgbbo"
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
    subnet_id = yandex_vpc_subnet.subnet-a.id
    nat       = true
  }
  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/ssh-key-1766963389342.pub")}"
  }
}

## Кластер k8s
#resource "yandex_managed_kubernetes_cluster" "cluster" {
#  name                = "k8s_cluster"
#  description         = "Кластер Kubernetess"
#  network_id          = yandex_vpc_network.network-main.id
#  master_version      = "1.33" # Рекомендуется Яндексом
#  maintenance_policy {
#    auto_upgrade = true
#  }
#}
#
## Группа нод кластера
#resource "yandex_managed_kubernetes_node_group" "node_group" {
#  name                      = "k8s_node_group"
#  cluster_id                = yandex_managed_kubernetes_cluster.cluster.id
#  scale_policy {
#    max_size = length(["ru-central1-a", "ru-central1-b"]) * 3 #зоны доступности умноженные на количество нод в каждой зоне
#    min_size = length(["ru-central1-a", "ru-central1-b"]) * 3 #зоны доступности умноженные на количество нод в каждой зоне
#  }
#  allocation_policy {
#    zones = ["ru-central1-a", "ru-central1-b"]
#  }
#  node_template {
#    platform_id = "standard-v2"
#    resources_spec {
#      memory = 8   # Кластер типа "Preview"
#      cores  = 2   # Кластер типа "Preview"
#    }
#    local_storage {
#      disk_type = "network-nvme"
#      disk_size = 10
#    }
#    image {
#      family = "k8s-nodes-image-family"
#    }
#    service_account_id = "ajehpp26k8qvn8iac0up" #boryan71-service-acc
#  }
#  depends_on       = [yandex_managed_kubernetes_cluster.cluster]
#}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}
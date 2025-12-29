# Переменные
# Основные

variable "cloud_id" {
	description = "ID облака"
	type = string
	}
	
variable "folder_id" {
	description = "ID каталога"
	type = string
	}
	
variable "default_zone" {
	description = "Зона доступности"
	type = string
	default = "ru-central1-a"
	}
	
# Для сети

variable "network_name" {
	description = ""
	type = string
	}
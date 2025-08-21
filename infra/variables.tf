# Define application resource group
variable "app_service_resource_group" {
  type        = string
  description = "The name of the Azure Resource Group to use."
  default     = ""
}

# Define application azure location
variable "location" {
  type        = string
  description = "The name of the Azure Location"
  default     = "westeurope"
}

# Define docker image name
variable "docker_image_name" {
  type        = string
  description = "The name of the Docker image"
  default     = ""
}

# Define app service app settings
variable "app_service_app_settings" {
  description = "App Service application settings (key-value pairs)"
  type        = map(string)
  default     = {}
  sensitive   = true
}

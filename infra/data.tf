# Generate reference to azure app service plan
data "azurerm_app_service_plan" "app_service_plan" {
  name                = "applications"
  resource_group_name = var.app_service_resource_group
}

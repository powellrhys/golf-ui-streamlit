# Define backend config
terraform {
  backend "azurerm" {
    resource_group_name   = "tfstate-rg"
    storage_account_name  = "powellrhystfstate"
    container_name        = "tfstate"
    key                   = "golf.tfstate"
  }
}

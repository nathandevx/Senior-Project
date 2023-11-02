from senior_project.utils import get_allowed_cities

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

PRODUCT_FORM_ERROR1 = "Status must be set to 'inactive' if stock is 0."
PRODUCT_FORM_ERROR2 = "Status must be set to 'inactive' if stock overflow is greater than 0."
CARTITEM_FORM_ERROR1 = "Ensure this value is greater than or equal to 1."
SHIPPING_ADDRESS_FORM_ERROR = f"We only deliver to the following cities: {', '.join(get_allowed_cities())}"
ORDER_FORM_ERROR = "estimated_delivery_date must be empty if order is canceled."

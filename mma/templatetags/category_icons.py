from django import template

register = template.Library()

CATEGORY_ICONS = {
    'groceries': 'fas fa-shopping-basket',
    'service': 'fas fa-concierge-bell',
    'job': 'fas fa-briefcase',
    'hardware': 'fas fa-tools',
    'electronics': 'fas fa-tv',
    'clothing': 'fas fa-tshirt',
    'furniture': 'fas fa-couch',
    'automotive': 'fas fa-car',
    'beauty_health': 'fas fa-heart',
    'toys': 'fas fa-puzzle-piece',
    'sports': 'fas fa-basketball-ball',
    'books': 'fas fa-book',
    'home_appliances': 'fas fa-blender',
    'stationery': 'fas fa-pen',
    'pharmacy': 'fas fa-prescription-bottle-alt',
    'jewelry': 'fas fa-gem',
    'footwear': 'fas fa-shoe-prints',
    'gardening': 'fas fa-seedling',
    'baby_products': 'fas fa-baby',
    'pet_supplies': 'fas fa-paw',
    'music_instruments': 'fas fa-guitar',
    'office_supplies': 'fas fa-briefcase',
    'gaming': 'fas fa-gamepad',
    'kitchenware': 'fas fa-utensils',
    'building_materials': 'fas fa-building',
    'tools': 'fas fa-wrench',
    'computer_accessories': 'fas fa-laptop',
}

@register.filter
def category_icon(category):
    """Return the icon class for the given category."""
    return CATEGORY_ICONS.get(category, 'fas fa-question-circle')  # Default icon

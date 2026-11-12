from django.db import migrations

# Starter catalog so the site has content on first run. Prices and visit
# lengths are left empty for the owner to set in the admin; the copy is a
# draft for the owner to review.
SERVICES = [
    {
        'slug': 'standard-clean',
        'name': 'Standard clean',
        'summary': 'Regular upkeep for a home that is already in good shape.',
        'description': (
            'A room-by-room clean that keeps your home ready for the week. '
            'Book it once, or every one, two, or four weeks.'
        ),
        'includes': (
            'Dust reachable surfaces and furniture\n'
            'Vacuum and mop all floors\n'
            'Clean kitchen counters, sink, and appliance fronts\n'
            'Clean and disinfect bathrooms\n'
            'Empty trash and replace liners\n'
            'Make beds and tidy common areas'
        ),
        'image': 'img/standard-clean.jpg',
        'image_alt': 'A cleaner mopping a wooden floor',
    },
    {
        'slug': 'deep-clean',
        'name': 'Deep clean',
        'summary': 'A top-to-bottom clean for a first visit or a seasonal reset.',
        'description': (
            'Everything in a standard clean, plus the detail work that builds up '
            'over time. A good first visit before regular cleans.'
        ),
        'includes': (
            'Everything in a standard clean\n'
            'Baseboards, door frames, and light switches\n'
            'Inside the microwave\n'
            'Kitchen cabinet fronts\n'
            'Tile and grout buildup in bathrooms\n'
            'Window sills and blinds'
        ),
        'image': 'img/deep-clean.jpg',
        'image_alt': 'A gloved hand wiping a white surface',
    },
    {
        'slug': 'move-in-move-out-clean',
        'name': 'Move-in or move-out clean',
        'summary': 'An empty home cleaned inside and out, ready for keys or a walkthrough.',
        'description': (
            'For tenants, owners, and landlords between occupants. The home should '
            'be empty of furniture and belongings.'
        ),
        'includes': (
            'Everything in a deep clean\n'
            'Inside cabinets, drawers, and closets\n'
            'Inside the refrigerator and oven\n'
            'Wipe down walls where marked\n'
            'Clean all floors, including under where furniture stood'
        ),
        'image': 'img/move-in-out.jpg',
        'image_alt': 'A cleaner carrying a caddy and broom up a staircase',
    },
    {
        'slug': 'post-renovation-clean',
        'name': 'Post-renovation clean',
        'summary': 'Removes construction dust and residue after a remodel.',
        'description': (
            'Fine dust settles everywhere after a renovation. This clean removes it '
            'from surfaces, fixtures, and floors so the new space is ready to use.'
        ),
        'includes': (
            'Dust all surfaces, ledges, and fixtures\n'
            'Wipe vents and light fixtures\n'
            'Remove stickers and residue from new fixtures\n'
            'Clean inside new cabinets and drawers\n'
            'Vacuum and mop all floors twice'
        ),
        'image': 'img/kitchen.jpg',
        'image_alt': 'A bright kitchen with white cabinets and stainless steel appliances',
    },
    {
        'slug': 'upholstery-refresh',
        'name': 'Upholstery refresh',
        'summary': 'Vacuuming and spot cleaning for sofas, chairs, and ottomans.',
        'description': (
            'Add it to any visit, or book it on its own. We vacuum fabric furniture '
            'and treat everyday spots.'
        ),
        'includes': (
            'Vacuum cushions, seams, and under cushions\n'
            'Spot clean everyday stains\n'
            'Deodorize fabric surfaces'
        ),
        'image': 'img/upholstery.jpg',
        'image_alt': 'A cleaner vacuuming a gray ottoman',
    },
]


def add_services(apps, schema_editor):
    Service = apps.get_model('catalog', 'Service')
    for order, data in enumerate(SERVICES, start=1):
        Service.objects.get_or_create(slug=data['slug'], defaults={**data, 'sort_order': order * 10})


def remove_services(apps, schema_editor):
    Service = apps.get_model('catalog', 'Service')
    Service.objects.filter(slug__in=[data['slug'] for data in SERVICES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_enable_row_level_security'),
    ]

    operations = [
        migrations.RunPython(add_services, remove_services),
    ]

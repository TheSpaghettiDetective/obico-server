from django.db import migrations, models
import django.db.models.deletion


def to_one_syndicate_per_site(apps, schema_editor):
    # A request took its site's first syndicate (lowest id), so that one is kept.
    # A site in none, possible on servers set up before June 2024 that never ran
    # `manage.py site --fix`, gets the first syndicate, as that command gives it:
    # every signed-in request now looks up its host's syndicate.
    Site = apps.get_model('sites', 'Site')
    Syndicate = apps.get_model('app', 'Syndicate')
    SiteSyndicate = apps.get_model('app', 'SiteSyndicate')
    first = Syndicate.objects.order_by('id').first()
    for site in Site.objects.all():
        syndicate = site.syndicates.order_by('id').first() or first
        if syndicate:
            SiteSyndicate.objects.create(site=site, syndicate=syndicate)


def to_sites_of_syndicates(apps, schema_editor):
    SiteSyndicate = apps.get_model('app', 'SiteSyndicate')
    for link in SiteSyndicate.objects.all():
        link.syndicate.sites.add(link.site)


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('app', '0085_printerprediction_normalized_p'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSyndicate',
            fields=[
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True,
                                              related_name='site_syndicate', serialize=False, to='sites.site')),
                ('syndicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                related_name='site_syndicates', to='app.syndicate')),
            ],
        ),
        migrations.RunPython(to_one_syndicate_per_site, to_sites_of_syndicates),
        migrations.RemoveField(
            model_name='syndicate',
            name='sites',
        ),
    ]

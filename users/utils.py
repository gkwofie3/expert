from django.apps import apps
from django.db.models import ForeignKey

def clean_orphaned_foreign_keys():
    """
    This function iterates through all models in all apps,
    finds ForeignKey fields, and removes orphaned references.
    """
    for model in apps.get_models():
        for field in model._meta.fields:
            if isinstance(field, ForeignKey):
                related_model = field.related_model
                foreign_key_name = field.name
                
                # Find and clean orphaned entries
                orphaned_entries = model.objects.exclude(**{
                    f"{foreign_key_name}__in": related_model.objects.all()
                })
                
                if orphaned_entries.exists():
                    print(f"Cleaning {orphaned_entries.count()} orphaned references in {model.__name__}.{foreign_key_name}")
                    
                    # Set NULL if the field is nullable, else delete the records
                    if field.null:
                        orphaned_entries.update(**{foreign_key_name: None})
                    else:
                        orphaned_entries.delete()

    print("Foreign key cleanup completed.")


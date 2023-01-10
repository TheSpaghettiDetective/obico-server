import django
from whitenoise.storage import CompressedManifestStaticFilesStorage, MissingFileError


class CustomCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    if django.VERSION < (4, 0):
        patterns = CompressedManifestStaticFilesStorage.patterns + (
            (
                "*.js",
                (
                    (
                        r"(?m)^(//# (?-i:sourceMappingURL)=(.*))$",
                        "//# sourceMappingURL=%s",
                    ),
                ),
            ),
            (
                "*.css",
                (
                    (
                        r"(?m)^(/\*#[ \t](?-i:sourceMappingURL)=(.*)[ \t]*\*/)$",
                        "/*# sourceMappingURL=%s */",
                    ),
                ),
            ),
        )
    elif django.VERSION < (4, 1):
        # Django 4.0 switched to named patterns
        patterns = CompressedManifestStaticFilesStorage.patterns + (
            (
                "*.css",
                (
                    (
                        r"(?m)^(?P<matched>/\*#[ \t](?-i:sourceMappingURL)=(?P<url>.*)[ \t]*\*/)$",
                        "/*# sourceMappingURL=%(url)s */",
                    ),
                ),
            ),
        )
    else:
        raise AssertionError(
            "The above backported custom patterns are no longer required."
        )

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            import logging
            if isinstance(processed, MissingFileError) and name + ".map" in str(processed):
                logging.error(f"Cannot post-process map file for {name}")
                continue

            yield name, hashed_name, processed

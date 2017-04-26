class FileLoader:

    def _load_post_file_data(self, file_data):
        """
        Import content from raw file data.
        """

        fmt = self.loader_format_from_filename(file_data.name)
        self.load_data(file_data, format=fmt)
        self.__imported_data = dict(self.__dict__)

        logger.info('Imported question "%s" from file "%s"' %
                    (self.title, self.import_file.name))

        # We fake POST data after loading data from file in order to make the
        # required fields validate. This part constructs a dictionary that
        # will be used to feed a fake POST data in the QuestionAdminModelForm
        # instance
        fake_post_data = {
            'title': self.title or _('Untitled'),
            'short_description': self.short_description or _('untitled'),
        }

        for field in self.OPTIONAL_IMPORT_FIELDS:
            if getattr(self, field, None):
                fake_post_data[field] = getattr(self, field)

        base_slug = slugify(fake_post_data['title'])
        auto_generated_slug = self._get_autogenerated_slug(base_slug)
        fake_post_data['slug'] = auto_generated_slug
        return fake_post_data

    def _loader_format_from_filename(self, name):
        """
        Returns a string with the loader method from the file extension
        """

        _, ext = os.path.splitext(name)
        ext = ext.lstrip('.')
        return self.EXT_TO_METHOD_CONVERSIONS.get(ext, ext)

    def _load_data(self, data, format='yaml'):
        """
        Load data from the given file or string object using the specified
        method.
        """

        try:
            loader = getattr(self, 'load_%s_data' % format)
        except AttributeError:
            raise ValueError('format %r is not implemented' % format)
        return loader(data)

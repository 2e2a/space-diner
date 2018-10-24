class Thing:

    def __str__(self):
        return self.name if hasattr(self, 'name') else super().__str__(self)

    def debug(self):
        for k, v in self.__dict__.items():
            if not k.startswith('__') and not callable(k):
                if isinstance(v, list):
                    v = ', '.join(str(e) for e in v)
                print('{}: {}'.format(k, v))

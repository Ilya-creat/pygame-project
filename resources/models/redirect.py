class Redirect:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Redirect, cls).__new__(cls)
        return cls.instance

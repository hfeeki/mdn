import jingo

def handle403(request):
    """A 403 message that looks nicer than the normal Apache forbidden page."""

    return jingo.render(request, '403.html', status=403)

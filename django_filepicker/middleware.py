import re
import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


class URLFileMapperMiddleware(object):
    """
    This middleware will take any Filepicker.io urls that are posted to the server via a POST
    and put a matching File object into request.FILES. This way, if you're used to grabbing files out of
    request.FILES, you don't have to change your backend code when using the filepicker.io widgets.

    This middleware is rather agressive in that it will automatically fetch any and all filepicker
    urls passed to the server, so if you are already processing the files via FPFileField or similar
    this functionality is redundant

    Note that the original filepicker.io url will still be available in POST if you need it.
    """
    filepicker_url_regex = re.compile(
            r'https?:\/\/www.filepicker.io\/api\/file\/.*')

    def process_request(self, request):
        #Iterate over GET or POST data, search for filepicker.io urls
        for key, val in request.POST.items():
            if self.isFilepickerURL(val):
                    url_fp = urllib2.urlopen(val)
                    disposition = url_fp.info().getheader('Content-Disposition')
                    if disposition:
                        name = disposition.rpartition("filename=")[2].strip('" ')
                    else:
                        name = "fp-file"

                    fp_data = NamedTemporaryFile(delete=True)
                    fp_data.write(url_fp.read())
                    fp_data.flush()

                    request.FILES[key] = File(fp_data, name=name)

    def isFilepickerURL(self, val):
        return bool(self.filepicker_url_regex.match(val))

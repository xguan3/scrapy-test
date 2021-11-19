
def make_request(url, abc, meta):
    abc({'meta': meta})
    # parse_image({ 'meta': meta })
    # magic

def parse_image(response):
    print(response)

request = make_request('https://google.com/favicon.png', parse_image, {'name': 'iris'})
    
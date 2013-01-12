# -*- coding: utf-8 -*-
"""
Add Header Images to context
=========================

"""
import logging
import pickle
import re

import flickr as api_client
from pelican import signals


flickr_regex = re.compile(r'<p>(\[flickr:id\=([0-9]+)\])</p>')
logger = logging.getLogger(__name__)


def setup_flickr(pelican):
    """Add Flickr api object to Pelican settings."""

    try:
        api_client.API_KEY = pelican.settings['FLICKR_API_KEY']
        api_client.API_SECRET = pelican.settings['FLICKR_API_SECRET']
    except KeyError:
        raise Exception('FLICKR_API_KEY and FLICKR_API_SECRET are '
            'required configuration settings.')

    pelican.settings['FLICKR_TAG_API_CLIENT'] = api_client
    pelican.settings.setdefault('FLICKR_TAG_CACHE_LOCATION',
        '/tmp/com.chrisstreeter.flickrtag-images.cache')


def replace_article_tags(generator):
    api = generator.context.get('FLICKR_TAG_API_CLIENT', None)
    if api is None:
        logger.error('Unable to get the Flickr API object')
        return

    tmp_file = generator.context.get('FLICKR_TAG_CACHE_LOCATION')

    photo_ids = set([])
    logger.info('Parsing articles for photo ids...')
    for article in generator.articles:
        for match in flickr_regex.findall(article._content):
            photo_ids.add(match[1])

    logger.info('Found %d photo ids in the articles' % len(photo_ids))

    try:
        with open(tmp_file, 'r') as f:
            photo_mapping = pickle.load(f)
    except (IOError, EOFError):
        photo_mapping = {}
    else:
        # Get the difference of photo_ids and what have cached
        cached_ids = set(photo_mapping.keys())
        photo_ids = list(set(photo_ids) - cached_ids)

    if photo_ids:
        logger.info('Fetching photo information from Flickr...')
        for id in photo_ids:
            logger.info('Fetching photo information for %s' % id)
            photo = api.Photo(id=id)
            # Trigger the API call...
            photo_mapping[id] = {
                'title': photo.title,
                'raw_url': photo.getMedium(),
                'url': photo.url,
            }

        with open(tmp_file, 'w') as f:
            pickle.dump(photo_mapping, f)
    else:
        logger.info('Found pickled photo mapping')

    logger.info('Inserting photo information into articles...')
    for article in generator.articles:
        for match in flickr_regex.findall(article._content):
            fid = match[1]
            if fid not in photo_mapping:
                logger.error('Could not find info for a photo!')
                continue

            replacement = """<p class="caption-container">
    <a class="caption" href="%(url)s" target="_blank">
        <img src="%(raw_url)s" alt="%(title)s" title="%(title)s" class="img-polaroid" />
    </a>
    <span class="caption-text muted">%(title)s</span>
</p>""" % photo_mapping[fid]

            article._content = article._content.replace(match[0], replacement)


def register():
    """Plugin registration."""

    signals.initialized.connect(setup_flickr)

    signals.article_generator_finalized.connect(replace_article_tags)

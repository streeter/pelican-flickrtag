# -*- coding: utf-8 -*-
"""
Embed Flickr Images in Pelican Articles and Pages
=================================================

"""
import logging
import pickle
import re

import pelican_flickrtag.flickr as api_client

from pelican import signals

flickr_regex = re.compile(r'<p>(\[flickr:id\=([0-9]+)(?:,title\=(.+))?\])</p>')
default_template = """<p class="caption-container">
    <a class="caption" href="{{url}}" target="_blank">
        <img src="{{raw_url}}"
            alt="{{title}}"
            title="{{title}}"
            class="img-polaroid"
            {% if FLICKR_TAG_INCLUDE_DIMENSIONS %}
                width="{{width}}"
                height="{{height}}"
            {% endif %} />
    </a>
    <span class="caption-text muted">{{title}}</span>
</p>"""

logger = logging.getLogger(__name__)


def setup_flickr(generator):
    """Add Flickr api object to Pelican settings."""

    for key in ('TOKEN', 'KEY', 'SECRET'):
        try:
            value = generator.settings['FLICKR_API_' + key]
            setattr(api_client, 'API_' + key, value)
        except KeyError:
            logger.warning('[flickrtag]: FLICKR_API_%s is not defined in the configuration' % key)

    generator.flickr_api_client = api_client

    generator.settings.setdefault(
        'FLICKR_TAG_CACHE_LOCATION',
        '/tmp/com.chrisstreeter.flickrtag-images.cache')
    generator.settings.setdefault('FLICKR_TAG_INCLUDE_DIMENSIONS', False)
    generator.settings.setdefault('FLICKR_TAG_IMAGE_SIZE', 'Medium 640')


def url_for_alias(photo, alias):
    if alias == 'Medium 640':
        url = photo.getMedium640()
    else:
        url = photo.getMedium()
    url = url.replace('http:', '').replace('https:', '')
    return url


def size_for_alias(sizes, alias):
    if alias not in ('Medium 640', 'Medium'):
        alias = 'Medium'
    return [s for s in sizes if s['label'] == alias][0]


def replace_tags(generator, documents):
    from jinja2 import Template

    api = generator.flickr_api_client
    if api is None:
        logger.error('[flickrtag]: Unable to get the Flickr API object')
        return

    tmp_file = generator.settings['FLICKR_TAG_CACHE_LOCATION']

    include_dimensions = generator.settings['FLICKR_TAG_INCLUDE_DIMENSIONS']
    size_alias = generator.settings['FLICKR_TAG_IMAGE_SIZE']

    photo_ids = set([])
    for document in documents:
        for match in flickr_regex.findall(document._content):
            id, title = match[1:3]
            fid = '{}-{}'.format(id, title) if title else id
            photo_ids.add(fid)

    photo_ids_found = len(photo_ids)

    try:
        with open(tmp_file, 'rb') as f:
            photo_mapping = pickle.load(f)
    except (IOError, EOFError, ValueError):
        photo_mapping = {}
    else:
        # Get the difference of photo_ids and what have cached
        cached_ids = set(photo_mapping.keys())
        photo_ids = list(set(photo_ids) - cached_ids)

    if photo_ids:
        logger.info('[flickrtag]: Fetching photo information from Flickr...')
        for fid in photo_ids:
            logger.info('[flickrtag]: Fetching photo information for %s' % fid)
            id, title = (fid.split('-', 1) + [''])[:2]
            photo = api.Photo(id=int(id))
            # Trigger the API call...
            photo_mapping[fid] = {
                'title': title or photo.title,
                'raw_url': url_for_alias(photo, size_alias),
                'url': photo.url,
            }

            if include_dimensions:
                sizes = photo.getSizes()
                size = size_for_alias(sizes, size_alias)
                photo_mapping[fid]['width'] = size['width']
                photo_mapping[fid]['height'] = size['height']

        with open(tmp_file, 'wb') as f:
            pickle.dump(photo_mapping, f)
    else:
        logger.info('[flickrtag]: Found pickled photo mapping')

    # See if a custom template was provided
    template_name = generator.settings['FLICKR_TAG_TEMPLATE_NAME']
    if template_name is not None:
        # There's a custom template
        try:
            template = generator.get_template(template_name)
        except Exception:
            logger.error('[flickrtag]: Unable to find the custom template %s' % template_name)
            template = Template(default_template)
    else:
        template = Template(default_template)

    logger.info('[flickrtag]: Inserting photo information...')
    for document in documents:
        for match in flickr_regex.findall(document._content):
            fid, title = match[1:3]
            if title:
                fid = '{}-{}'.format(fid, title)
            if fid not in photo_mapping:
                logger.error('[flickrtag]: Could not find info for a photo!')
                continue

            # Create a context to render with
            context = generator.context.copy()
            context.update(photo_mapping[fid])

            # Render the template
            replacement = template.render(context)

            document._content = document._content.replace(match[0], replacement)

    return photo_ids_found


def replace_article_tags(generator):
    logger.info('[flickrtag]: Parsing articles for photo ids...')
    total = replace_tags(generator, generator.articles)
    logger.info('[flickrtag]: Found %d photos ids in articles' % total)


def replace_page_tags(generator):
    logger.info('[flickrtag]: Parsing pages for photo ids...')
    total = replace_tags(generator, generator.pages)
    logger.info('[flickrtag]: Found %d photos ids in pages' % total)


def register():
    """Plugin registration."""
    signals.generator_init.connect(setup_flickr)

    signals.article_generator_finalized.connect(replace_article_tags)
    signals.page_generator_finalized.connect(replace_page_tags)

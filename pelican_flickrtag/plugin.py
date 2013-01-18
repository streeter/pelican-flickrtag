# -*- coding: utf-8 -*-
"""
Embed Flickr Images in Pelican Articles
=======================================

"""
import logging
import pickle
import re

import flickr as api_client


flickr_regex = re.compile(r'<p>(\[flickr:id\=([0-9]+)\])</p>')
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


def setup_flickr(pelican):
    """Add Flickr api object to Pelican settings."""

    for key in ('TOKEN', 'KEY', 'SECRET'):
        try:
            value = pelican.settings['FLICKR_API_' + key]
            setattr(api_client, 'API_' + key, value)
        except KeyError:
            logger.warning('[flickrtag]: FLICKR_API_%s is not defined in the configuration' % key)

    pelican.settings['FLICKR_TAG_API_CLIENT'] = api_client
    pelican.settings.setdefault('FLICKR_TAG_CACHE_LOCATION',
        '/tmp/com.chrisstreeter.flickrtag-images.cache')
    pelican.settings.setdefault('FLICKR_TAG_INCLUDE_DIMENSIONS', False)
    pelican.settings.setdefault('FLICKR_TAG_IMAGE_SIZE', 'Medium 640')


def url_for_alias(photo, alias):
    if alias == 'Medium 640':
        return photo.getMedium640()
    else:
        return photo.getMedium()


def size_for_alias(sizes, alias):
    if alias not in ('Medium 640', 'Medium'):
        alias = 'Medium'
    return [s for s in sizes if s['label'] == alias][0]


def replace_article_tags(generator):
    from jinja2 import Template

    api = generator.context.get('FLICKR_TAG_API_CLIENT', None)
    if api is None:
        logger.error('[flickrtag]: Unable to get the Flickr API object')
        return

    tmp_file = generator.context.get('FLICKR_TAG_CACHE_LOCATION')

    include_dimensions = generator.context.get('FLICKR_TAG_INCLUDE_DIMENSIONS')
    size_alias = generator.context.get('FLICKR_TAG_IMAGE_SIZE')

    photo_ids = set([])
    logger.info('[flickrtag]: Parsing articles for photo ids...')
    for article in generator.articles:
        for match in flickr_regex.findall(article._content):
            photo_ids.add(match[1])

    logger.info('[flickrtag]: Found %d photo ids in the articles' % len(photo_ids))

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
        logger.info('[flickrtag]: Fetching photo information from Flickr...')
        for id in photo_ids:
            logger.info('[flickrtag]: Fetching photo information for %s' % id)
            photo = api.Photo(id=id)
            # Trigger the API call...
            photo_mapping[id] = {
                'title': photo.title,
                'raw_url': url_for_alias(photo, size_alias),
                'url': photo.url,
            }

            if include_dimensions:
                sizes = photo.getSizes()
                size = size_for_alias(sizes, size_alias)
                photo_mapping[id]['width'] = size['width']
                photo_mapping[id]['height'] = size['height']

        with open(tmp_file, 'w') as f:
            pickle.dump(photo_mapping, f)
    else:
        logger.info('[flickrtag]: Found pickled photo mapping')

    # See if a custom template was provided
    template_name = generator.context.get('FLICKR_TAG_TEMPLATE_NAME')
    if template_name is not None:
        # There's a custom template
        try:
            template = generator.get_template(template_name)
        except Exception:
            logger.error('[flickrtag]: Unable to find the custom template %s' % template_name)
            template = Template(default_template)
    else:
        template = Template(default_template)

    logger.info('[flickrtag]: Inserting photo information into articles...')
    for article in generator.articles:
        for match in flickr_regex.findall(article._content):
            fid = match[1]
            if fid not in photo_mapping:
                logger.error('[flickrtag]: Could not find info for a photo!')
                continue

            # Create a context to render with
            context = generator.context.copy()
            context.update(photo_mapping[fid])

            # Render the template
            replacement = template.render(context)

            article._content = article._content.replace(match[0], replacement)


def register():
    """Plugin registration."""
    from pelican import signals

    signals.initialized.connect(setup_flickr)

    signals.article_generator_finalized.connect(replace_article_tags)

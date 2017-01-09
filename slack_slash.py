# Slack API Calls
def post_slack_data(text='', attachments=[], response_type='in_channel'):
    """compiles the attachments and generates the json data for a slack post"""
    data = {'attachments':attachments,
            'response_type': response_type,
            'text': text}
    return jsonify(data)


def slack_podcast_doesnt_exist():
    msg_text = ':no_entry_sign: *INVALID PODCAST NAME*: \
    please use a podcast from the list.\n'

    podcast_text_list = ['- {} - {}'.format(x[0], x[1]) for x in podcasts]
    podcasts_text = '\n'.join(podcast_text_list)
    text = msg_text + podcasts_text
    return post_slack_data(text=text, response_type='ephemeral')

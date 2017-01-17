podcasts=('pitpodcast', 'pitreflections')

# Slack API Calls
def post_slack_data(text='', attachments=[], response_type='in_channel'):
    """compiles the attachments and generates the json data for a slack post"""
    data = {'attachments':attachments,
            'response_type': response_type,
            'text': text}
    return jsonify(data)

     return 

def validate(valid_token, text_check=podcasts):
    
    def check_token(f):
        if not form['text']:
            return 'empty text'
            
        else:
            good_token = form['token'] == valid_token
            valid_podcast = form['text'] in text_check
            
            if all((good_token, valid_podcast)):
                return f()
                
            else:
                msg_text = ':no_entry_sign: *INVALID PODCAST NAME*: \
                please use a podcast from the list.\n'
                podcast_text_list = ['- {} - {}'.format(x[0], x[1]) for x in podcasts]
                podcasts_text = '\n'.join(podcast_text_list)
                text = msg_text + podcasts_text
                return  post_slack_data(text=text, response_type='ephemeral')

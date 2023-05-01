from bs4 import BeautifulSoup
import json, os, glob, re

result = []

def safe_get(el, prop):
    if el and el.has_attr(prop):
        return el[prop]
    return ''

def remove_all_but_digits_and_parse_int(x):
    return int(re.sub('\D', '', x) or '-1') # -1 for cases then nothing remains

def process_files_in_dir_by_glob(path, selector):
    pattern = os.path.join(path, selector)
    files = glob.glob(pattern)
    files.insert(0, files.pop()) # move file without number in bracets to the beginning (not tested with timestamps (then more than 100 files downloaded with the same name)), remove if order is unrelevant
    for file in files:
        process_file(file)
    
def process_file(path):
    process_posts(json.load(open(path, encoding='utf-8')))

def process_posts(posts):
    for post in posts:
        soup = BeautifulSoup(post, "html.parser")
        comment_author = soup.select_one('.author')
        is_comment = comment_author != None
        is_post = not is_comment
        if is_post:
            id_ = soup.select_one('a.PostHeaderTitle__authorLink')['data-post-id']
            text_el = soup.select_one('.wall_post_text')
            show_more = text_el.select_one('.PostTextMore')
            show_more and show_more.decompose() # clear 'Показать еще'
            hidden_part_span = text_el.select_one('span')
            hidden_part_span and hidden_part_span.replace_with_children() # clear odd \n
            text = text_el.get_text('\n')
            subtitle_from_el = soup.select_one('a.PostHeaderSubtitle__item')
            subtitle_from = safe_get(subtitle_from_el, 'href')
            when = soup.select_one('time').get_text()
            imgs_data = [json.loads(x['data-options'])['temp'] for x in soup.select('[data-options]')]
            audios_data = [json.loads(x['data-audio']) for x in soup.select('[data-audio]')]
            lincs = [safe_get(x, 'href') for x in soup.select('a')]
            away_lincs = [x for x in lincs if x.startswith('/away.php')]
            videos_lincs = [x for x in lincs if x.startswith('/video') and x[6] in '-0123456789'] # is 7'th symbol always present?
            other_lincs = [safe_get(x, 'href') for x in soup.select_one('.wall_text').select('a')]
            other_lincs = [x for x in other_lincs if not x.startswith('/feed?section=search&amp;q=%23') and x not in other_lincs and x not in videoLincs] # remove search tags and lincs from other cats
            votingEl = soup.select_one('.media_voting')
            votingData = {}
            if votingEl:
                question = votingEl.select_one(".media_voting_question").get_text();
                info = votingEl.select_one(".media_voting_info").get_text();
                options = [x.get_text() for x in votingEl.select(".media_voting_option_text")]
                votersCount = remove_all_but_digits_and_parse_int(votingEl.select_one("._media_voting_footer_voted_text").get_text());
                firstVoters = [safe_get(x, 'href') for x in votingEl.select(".media_voting_footer_voted_friend")]
                votingData = {"question" : question, "info" : info, "options" : options, "voters_count" : votersCount, "first_voters" : firstVoters}    
            stats = [remove_all_but_digits_and_parse_int(x.get_text()) for x in soup.select('.PostBottomAction__count')]
            lices = stats[0]
            comments = stats[1] if len(stats) == 3 else 0
            reposts = stats[2] if len(stats) == 3 else (stats[1] if len(stats) == 2 else 0) # reposts can be banned?
            resultPost = {'id' : id_, "from" : subtitle_from, "text" : text, 'when' : when, 'imgs' : imgs_data, 'videos' : videos_lincs, 'audios' : audios_data, 'lincs' : {'away' : away_lincs, 'other' : other_lincs}, 'comments' : [], "voting_data" : votingData, 'stats' : {'lices' : lices, 'comments' : comments, 'reposts' : reposts}}
            result.append(resultPost)
        elif is_comment:
            from_ = soup.select_one('.author').get_text()
            text_el = soup.select_one('.wall_reply_text')
            text = text_el and text_el.get_text() or '' # no sticers support for now
            when = soup.select_one('.rel_date').get_text()
            result[-1]['comments'].append({'from' : from_, 'text' : text, 'when' : when})
    
path = '/media/paul/B0701CFA701CC94C/Users/Paul/Downloads/'
selector = 'psyamour_part*.json'
# process_files_in_dir_by_glob(path, selector)
process_file('/media/paul/B0701CFA701CC94C/Users/Paul/Downloads/psyamour_part (5).json')
